import httpx

from contextlib import asynccontextmanager
from fastapi import FastAPI

from .router import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=50, max_connections=100)
    )

    yield {"http_client": http_client}

    await http_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api/v2/workflows")


@app.get("/api/v2/workflows/health")
def health_check():
    return {"status": "ok"}
