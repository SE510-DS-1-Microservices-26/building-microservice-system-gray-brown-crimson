# Polling System — Microservices

A distributed polling platform where users create polls and submit votes, built as a set of independent Python microservices that communicate over HTTP and RabbitMQ.

## What the system does

Users interact with a single gateway endpoint to:

- **Create and manage polls** — define questions, options, and lifecycle status
- **Submit votes** — answer poll questions; the workflow service ensures each submission is consistent and idempotent
- **Receive notifications** — get notified when poll-related events occur
- **Manage their account** — create, update, and delete user records

## Services

| Service | Responsibility |
|---|---|
| **nginx** (gateway) | Reverse proxy — single entry point for all inbound traffic |
| **core-service** | Polls and votes — CRUD operations and business rules |
| **users-service** | User accounts — registration, lookup, and management |
| **workflow-service** | Vote orchestration — runs the Saga and ensures consistency |
| **notification-service** | Async notifications — consumes RabbitMQ events from core-service |

### How voting works

Voting is not a simple write — it is a multi-step workflow managed exclusively by `workflow-service` using a **Saga pattern**:

1. Check whether the user already voted or has an in-progress submission.
2. Verify the poll is active (call `core-service`).
3. Save the vote (call `core-service`).
4. Re-verify the poll is still active after the write.
5. If the poll became inactive between steps 3 and 4, **compensate** by cancelling the vote.
6. Mark the workflow `COMPLETED` or `FAILED` with an error message stored for audit.

This guarantees the database is never left in an inconsistent state even if the poll status changes mid-flight.

## Infrastructure

- **PostgreSQL 16** — each service has its own isolated database (database-per-service pattern)
- **RabbitMQ 3** — `core-service` publishes `core-item.created` events; `notification-service` consumes them asynchronously
- **NGINX** — routes `/api/v2/core`, `/api/v2/users`, and `/api/v2/workflows` to the correct backend service

## Tech stack

- **Python 3.12**, **FastAPI**, **SQLAlchemy 2**, **Alembic** (per-service migrations)
- **asyncpg** / **psycopg3** for async and sync PostgreSQL drivers
- **FastStream** + **aio-pika** for RabbitMQ integration
- **httpx** for inter-service HTTP calls
- **Pydantic v2** + **pydantic-settings** for validation and configuration
- **uv** as the package manager, **mypy** + **ruff** for static analysis and linting

## Project layout

```
src/
├── core_service/        # Polls & votes API
├── users_service/       # User management API
├── notification_service/# RabbitMQ consumer + notification persistence
├── workflow_service/    # Vote workflow orchestration (Saga)
│   └── app/
│       ├── api/         # FastAPI routers
│       ├── core/        # Domain model, application services, protocols
│       └── shared/      # Settings and dependencies
└── shared/              # Shared utilities across services

k8s/                     # Kubernetes manifests (namespace → infra → services → ingress)
nginx/                   # NGINX configuration
```

Each service follows a **Clean Architecture** layout: `api` → `core/application` → `core/domain`, with infrastructure adapters behind protocol interfaces so the domain never imports from the infrastructure layer.

## API reference

All routes are served through the gateway on port `80`.

### core-service — `/api/v2/core`

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v2/core/health` | Health check |
| `POST` | `/api/v2/core/polls/` | Create a poll |
| `GET` | `/api/v2/core/polls/{poll_id}` | Fetch a poll by ID |
| `PATCH` | `/api/v2/core/polls/{poll_id}/status` | Update poll status |
| `PUT` | `/api/v2/core/polls/{poll_id}` | Update poll data |
| `DELETE` | `/api/v2/core/polls/{poll_id}` | Delete a poll |
| `GET` | `/api/v2/core/votes/{poll_id}` | List votes for a poll |
| `POST` | `/api/v2/core/votes/{poll_id}` | Add a vote |
| `GET` | `/api/v2/core/votes/{poll_id}/user/{user_id}` | Check if a user voted |
| `DELETE` | `/api/v2/core/votes/vote/{vote_id}` | Cancel a vote |

### users-service — `/api/v2/users`

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v2/users/health` | Health check |
| `POST` | `/api/v2/users/` | Create a user |
| `GET` | `/api/v2/users/{user_id}` | Fetch a user |
| `PUT` | `/api/v2/users/{user_id}` | Update a user |
| `DELETE` | `/api/v2/users/{user_id}` | Delete a user |

### workflow-service — `/api/v2/workflows`

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v2/workflows/health` | Health check |
| `POST` | `/api/v2/workflows/vote` | Start a vote workflow |
| `GET` | `/api/v2/workflows/{workflow_id}` | Get workflow status |

> **Note:** Always use `/api/v2/workflows/vote` to submit votes — never call `core-service` directly. The workflow service owns the consistency guarantees.

## Running locally with Docker Compose

```bash
docker compose up --build
```

This starts all four services, four PostgreSQL databases, RabbitMQ, and NGINX. The gateway is available at `http://localhost`.

RabbitMQ management UI: `http://localhost:15672` (guest / guest)

## Deploying on Kubernetes

### 1. Build and load images

From the repository root:

```bash
docker build -t core-service:latest         -f src/core_service/Dockerfile .
docker build -t users-service:latest        -f src/users_service/Dockerfile .
docker build -t notification-service:latest -f src/notification_service/Dockerfile .
docker build -t workflow-service:latest     -f src/workflow_service/Dockerfile .
```

If using [kind](https://kind.sigs.k8s.io/) for a local cluster:

```bash
kind create cluster                          # create a cluster if you don't have one
kind load docker-image core-service:latest
kind load docker-image users-service:latest
kind load docker-image notification-service:latest
kind load docker-image workflow-service:latest
```

### 2. Apply the manifests

```bash
kubectl apply -f k8s/
```

Manifests are numbered in dependency order — namespace and infra come up before any application service starts. Check the rollout:

```bash
kubectl get pods -n microservices
kubectl get svc -n microservices
```

### 3. Reach the gateway

The Ingress uses the hostname `microservices.local`. With kind, use port-forwarding:

```bash
kubectl port-forward svc/gateway 8080:80 -n microservices
```

Then hit any endpoint at `http://localhost:8080`:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/v2/workflows/health
```

For a real cluster, add the Ingress IP to `/etc/hosts` as `microservices.local` and use that hostname instead.

### 4. Verify workflow success and failure

**Success** — create a poll, submit a vote, check the workflow state:

```bash
# start a vote workflow
curl -s -X POST http://localhost:8080/api/v2/workflows/vote \
  -H "Content-Type: application/json" \
  -d '{"poll_id": "<poll_id>", "user_id": "<user_id>", "answers": [{"question_id": "<question_id>", "selected_option": "Python"}]}' | jq .

# poll result — should be COMPLETED
curl -s http://localhost:8080/api/v2/workflows/<workflow_id> | jq '{state, vote_id}'
```

**Failure** — close the poll first, then try to vote:

```bash
curl -s -X PATCH http://localhost:8080/api/v2/core/polls/<poll_id>/status \
  -H "Content-Type: application/json" \
  -d '{"status": "closed"}'

curl -s http://localhost:8080/api/v2/workflows/<workflow_id> | jq '{state, error}'
# → { "state": "FAILED", "error": "Poll is not active" }
```

Submitting a duplicate vote returns HTTP 409 immediately without touching the vote store.

---

## Practice 6 — RabbitMQ Integration

### What was built

- **Event publishing** — after a vote or poll item is created, `core-service` publishes a `core-item.created` event to the `core` exchange (DIRECT, durable) with the routing key `core-item.created`. Messages are marked `PERSISTENT` so they survive a RabbitMQ restart. The active `X-Correlation-Id` is forwarded as a message header.
- **Event consumption** — `notification-service` is a standalone **FastStream** app that subscribes to the `notifications.core-item.created` queue bound to the same exchange and routing key. On each delivery it parses the payload, saves a notification record, and logs the `event_id` and `correlation_id`.
- **Idempotency** — `NotificationRepository.save()` uses a PostgreSQL `INSERT ... ON CONFLICT (event_id) DO NOTHING`. If RabbitMQ redelivers a message after a crash or restart, the duplicate insert is silently ignored — no duplicate notification records are ever created.

### Event payload

Every `core-item.created` message carries this JSON body:

```json
{
  "event_id":       "01j9z3ht-...",
  "occurred_at":    "2026-04-14T17:45:00.123456Z",
  "correlation_id": "a1b2c3d4-e5f6-...",
  "core_item_id":   "poll-uuid-here",
  "owner_user_id":  "user-uuid-here",
  "summary":        "Poll 'Favourite language' created"
}
```

### Verifying messages

Open the RabbitMQ management UI:

- **Docker Compose:** `http://localhost:15672` (guest / guest)
- **Kubernetes (port-forward):** `kubectl port-forward svc/rabbitmq 15672:15672 -n microservices`

Then navigate to **Queues → `notifications.core-item.created` → Get messages**. Create a poll to trigger a publish and confirm the message appears.

From the terminal:

```bash
# watch notification-service logs for processed events
kubectl logs -f deployment/notification-service -n microservices | grep "Notification processed"

# or with Docker Compose
docker compose logs -f notification_service
```

A successful delivery prints:
```
Notification processed: event_id=<uuid> core_item_id=<uuid> correlation_id=<uuid>
```

---

## Practice 7 — Workflow Service & Kubernetes

**What was built:**

- **Workflow Service (Saga)** — `workflow-service` orchestrates vote submission as a multi-step, stateful process. Workflow state (`PENDING` → `VOTE_SAVED` → `COMPLETED` / `FAILED`) is persisted to its own database after every step, so the system always knows where a workflow stopped. If the poll becomes inactive after a vote is saved, the service compensates by cancelling the vote automatically.

- **Kubernetes deployment** — all services and infrastructure were packaged as numbered manifests in `k8s/`. A dedicated namespace, per-service Secrets/ConfigMaps, PostgreSQL StatefulSets, and RabbitMQ deploy first; application Deployments follow with init containers that wait for their dependencies; an NGINX gateway and Ingress handle external traffic.

## Practice 8 — Resiliency, Correlation IDs & Kubernetes Operations

### Correlation ID end-to-end

Every HTTP request flowing through the system carries an `X-Correlation-Id` header. This is handled by `CorrelationIdMiddleware` in `src/shared/correlation.py`, mounted on every service:

- **Inbound** — if the request already has an `X-Correlation-Id`, the middleware uses it; otherwise it generates a new UUID.
- **Propagated** — inter-service HTTP calls attach the active correlation ID via `correlation_http_headers()`, so the same ID flows from the gateway through `workflow-service` into `core-service`.
- **Logged** — `CorrelationIdFilter` injects `correlation_id` into every log record, making it trivial to `grep` a single request trace across all service logs.
- **Returned** — the correlation ID is echoed back in the response header so clients can record it for support.

### Resiliency policies

Inter-service HTTP calls from `workflow-service` to `core-service` (poll checks and vote writes) go through `request_with_retry` in `http_retry.py`, backed by **Tenacity**:

- **3 attempts** total, with exponential backoff (0.3 s → 0.6 s → 2 s max).
- Retries on transient network errors (`TimeoutException`, `ConnectError`, `ReadError`) and server-side HTTP errors (5xx and 429).
- Non-transient errors (4xx) are not retried — they surface immediately as domain exceptions (`VoteServiceUnavailableException`, etc.) and cause the workflow to transition to `FAILED`.

### Scaling core-service

`core-service` runs with **3 replicas** in Kubernetes. Scale it up or down at runtime:

```bash
kubectl scale deployment core-service --replicas=5 -n microservices
kubectl get pods -n microservices -l app=core-service
```

Resource requests and limits are set on every Deployment so the scheduler can place pods reliably and prevent noisy-neighbour resource starvation:

| Service | CPU request | CPU limit | Memory request | Memory limit |
|---|---|---|---|---|
| core-service | 100m | 500m | 128Mi | 512Mi |
| workflow-service | 100m | 500m | 128Mi | 512Mi |
| gateway | 50m | 200m | 32Mi | 128Mi |

### Rolling updates and rollback

All Deployments use `RollingUpdate` strategy. `core-service` is configured with `maxUnavailable: 1` and `maxSurge: 1`, meaning at most one old pod goes down at a time while one new pod comes up — traffic is never fully interrupted.

**Performing a rollout** (after rebuilding and loading a new image):

```bash
# trigger a rollout by updating the image
kubectl set image deployment/core-service core-service=core-service:v2 -n microservices

# watch pods cycle
kubectl rollout status deployment/core-service -n microservices
```

**Rolling back** if the new version is unhealthy:

```bash
kubectl rollout undo deployment/core-service -n microservices

# confirm previous version is active
kubectl rollout status deployment/core-service -n microservices
```

Readiness probes (`/health`) ensure that new pods only receive traffic once they are fully started. If a pod never becomes ready, the rollout stalls and the old pods stay up — preventing a bad deploy from taking down the service.

---

