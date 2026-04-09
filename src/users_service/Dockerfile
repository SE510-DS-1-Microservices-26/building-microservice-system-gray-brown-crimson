FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --frozen


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY src/users_service/alembic/ ./alembic/
COPY alembic_users.ini ./alembic.ini

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8001

CMD alembic upgrade head && uvicorn src.users_service.app.api.main:app --host 0.0.0.0 --port 8001
