FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY app/ ./app/

ENV PATH="/app/.venv/bin:$PATH"
ENV DATABASE_URL="postgresql+psycopg://postgres:postgres@db:5432/polling"

EXPOSE 8080

CMD alembic upgrade head && uvicorn app.api.main:app --host 0.0.0.0 --port 8080
