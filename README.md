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

Everything runs in the `microservices` namespace. Check the rollout with:

```bash
kubectl get pods -n microservices
kubectl get svc -n microservices
```

## Production-readiness features

The Kubernetes manifests include several production-style configurations out of the box:

- **Resource requests and limits** on every Deployment to prevent resource starvation
- **Rolling update strategy** so new versions replace running pods gradually with no downtime
- **Readiness and liveness probes** via the `/health` endpoints — only healthy pods receive traffic, and crashing pods are restarted automatically
- **Init containers** that wait for databases and RabbitMQ to be ready before the application starts
- **Secrets and ConfigMaps** for clean separation between configuration and sensitive credentials

## RabbitMQ event flow

When a vote-related event completes in `core-service`, a message is published to the `core` exchange:

- **Event:** `core-item.created`
- **Queue:** `notifications.core-item.created`
- **Payload fields:** `event_id`, `occurred_at`, `correlation_id`, `core_item_id`, `owner_user_id`, `summary`

`notification-service` consumes events from this queue and persists a notification record. Processing is **idempotent** — redeliveries and retries will not create duplicate records.
