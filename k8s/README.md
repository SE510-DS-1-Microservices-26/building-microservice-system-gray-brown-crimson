## For k8s

### 1. Build container images (from repo root)

```bash
docker build -t core-service:latest -f src/core_service/Dockerfile .
docker build -t users-service:latest -f src/users_service/Dockerfile .
docker build -t notification-service:latest -f src/notification_service/Dockerfile .
docker build -t workflow-service:latest -f src/workflow_service/Dockerfile .
```

```bash
kind get clusters                    # should list at least one cluster
kind create cluster                  # if empty: creates "kind" with one control-plane node
```

If you use a custom name: `kind create cluster --name dev` and then pass `--name dev` to every `kind load` / `kubectl` context command.

Load images into that cluster:

```bash
kind load docker-image core-service:latest
kind load docker-image users-service:latest
kind load docker-image notification-service:latest
kind load docker-image workflow-service:latest
```

### 2. Apply manifests

```bash
kubectl apply -f k8s/
```

Namespace: `microservices`.

Check rollout:

```bash
kubectl get pods -n microservices
kubectl get svc -n microservices
```
