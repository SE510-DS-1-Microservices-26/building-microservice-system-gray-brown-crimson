import httpx

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.workflow_service.app.core.exception import (
    PollServiceUnavailableException,
    VoteServiceUnavailableException,
)
from src.workflow_service.app.core.logger import setup_logging
from src.shared.correlation import CorrelationIdMiddleware

from .router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(5.0),
        limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
    )
    app.state.http_client = http_client

    yield
    await http_client.aclose()


app = FastAPI(
    lifespan=lifespan,
    openapi_url="/api/v2/workflows/openapi.json",
    docs_url="/api/v2/workflows/docs",
    redoc_url="/api/v2/workflows/redoc",
)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(router, prefix="/api/v2/workflows")


@app.exception_handler(PollServiceUnavailableException)
async def poll_service_unavailable_handler(
    _: Request, exc: PollServiceUnavailableException
):
    if exc.timeout:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "error": "Gateway Timeout",
                "detail": "Core poll service did not respond in time.",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Service Unavailable",
            "detail": "Core poll service is unreachable.",
        },
    )


@app.exception_handler(VoteServiceUnavailableException)
async def vote_service_unavailable_handler(
    _: Request, exc: VoteServiceUnavailableException
):
    if exc.timeout:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "error": "Gateway Timeout",
                "detail": "Core vote service did not respond in time.",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Service Unavailable",
            "detail": "Core vote service is unreachable.",
        },
    )
