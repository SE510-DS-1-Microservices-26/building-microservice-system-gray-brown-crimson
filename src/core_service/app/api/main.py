import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.core_service.app.api.routers import votes, polls
from src.core_service.app.core.exception import (
    PollNotFoundException,
    PollNotEditableException,
    UserNotFoundException,
)
from src.core_service.app.core.logger import setup_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    logger = logging.getLogger("app.main")
    logger.info("Core Service API is initiating...")

    yield

    logger.info("Application is shutting down. Releasing resources...")


app = FastAPI(lifespan=lifespan)

app.include_router(polls.router)
app.include_router(votes.router)


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


@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(_: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not Found", "user_id": exc.user_id},
    )


@app.get("/api/v2/core/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/v2/core/health")
def health_check():
    return {"status": "ok"}
