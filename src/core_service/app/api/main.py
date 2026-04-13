import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.core_service.app.api.routers import votes, polls
from src.core_service.app.core.exception import (
    PollNotFoundException,
    PollNotEditableException,
    UserNotFoundException,
    UsersServiceTimeoutException,
    UsersServiceUnavailableException,
    VoteNotFoundException,
)
from src.core_service.app.core.infrastructure import RabbitMQPublisher
from src.core_service.app.core.infrastructure.outbox_relay import run_outbox_relay
from src.core_service.app.core.logger import setup_logging
from src.core_service.app.shared import settings
from src.shared.correlation import CorrelationIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger("app.main")
    logger.info("Core Service API is initiating...")

    publisher = RabbitMQPublisher(settings.rabbitmq_url)
    await publisher.connect()
    app.state.rabbitmq_publisher = publisher

    relay_task = asyncio.create_task(run_outbox_relay(publisher))

    yield

    relay_task.cancel()
    try:
        await relay_task
    except asyncio.CancelledError:
        pass
    await publisher.close()
    logger.info("Application is shutting down. Releasing resources...")


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(polls.router, prefix="/api/v2/core")
app.include_router(votes.router, prefix="/api/v2/core")


@app.exception_handler(PollNotFoundException)
async def poll_not_found_handler(_: Request, exc: PollNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not Found", "poll_id": exc.poll_id},
    )


@app.exception_handler(PollNotEditableException)
async def poll_not_editable_handler(_: Request, exc: PollNotEditableException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Poll Not Editable",
            "poll_id": exc.poll_id,
            "current_status": exc.status,
        },
    )


@app.exception_handler(VoteNotFoundException)
async def vote_not_found_handler(_: Request, exc: VoteNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not Found", "vote_id": exc.vote_id},
    )


@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(_: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "detail": f"User '{exc.user_id}' does not exist.",
        },
    )


@app.exception_handler(UsersServiceUnavailableException)
async def users_service_unavailable_handler(
    _: Request, __: UsersServiceUnavailableException
):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Service Unavailable",
            "detail": "Users service is unreachable.",
        },
    )


@app.exception_handler(UsersServiceTimeoutException)
async def users_service_timeout_handler(_: Request, __: UsersServiceTimeoutException):
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={
            "error": "Gateway Timeout",
            "detail": "Users service did not respond in time.",
        },
    )


@app.get("/api/v2/core/health")
def health_check():
    return {"status": "ok"}
