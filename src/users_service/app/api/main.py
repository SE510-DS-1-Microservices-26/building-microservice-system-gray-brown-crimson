import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.users_service.app.core.exception import UserNotFoundException
from src.users_service.app.core.logger import setup_logging
from src.users_service.app.api.routers import users


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    logger = logging.getLogger("app.main")
    logger.info("Users Service API is initiating...")
    
    yield
    
    logger.info("Application is shutting down. Releasing resources...")

    
app = FastAPI(lifespan=lifespan)

app.include_router(users.router)

@app.get("/api/v2/users")
def read_root():
    return {"Hello": "World"}

@app.get("/api/v2/users/health")
def health_check():
    return {"status": "ok"}
