import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.users_service.app.core.exception import UserNotFoundException
from src.users_service.app.core.logger import setup_logging
from src.users_service.app.api.routers import users
from src.shared.correlation import CorrelationIdMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    logger = logging.getLogger("app.main")
    logger.info("Users Service API is initiating...")

    yield

    logger.info("Application is shutting down. Releasing resources...")


app = FastAPI(
    lifespan=lifespan,
    openapi_url="/api/v2/users/openapi.json",
    docs_url="/api/v2/users/docs",
    redoc_url="/api/v2/users/redoc",
)
app.add_middleware(CorrelationIdMiddleware)


@app.get("/api/v2/users/health")
def health_check():
    return {"status": "ok"}


app.include_router(users.router, prefix="/api/v2/users")


@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(_: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "user_id": exc.user_id,
        },
    )
