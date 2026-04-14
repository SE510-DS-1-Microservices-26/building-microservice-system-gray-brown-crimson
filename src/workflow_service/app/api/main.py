import httpx

from contextlib import asynccontextmanager
from fastapi import FastAPI

from .router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=50, max_connections=100)
    )
    app.state.http_client = http_client

    yield
    await http_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api/v2/workflows")
