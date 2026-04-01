import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.routers import polls, votes, users
from app.core.exception import PollNotFoundException, UserNotFoundException
from app.core.logger import setup_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    logger = logging.getLogger("app.main")
    logger.info("Poll Service API is initiating...")
    
    yield
    
    logger.info("Application is shutting down. Releasing resources...")


app = FastAPI(lifespan=lifespan)

app.include_router(polls.router)
app.include_router(votes.router)
app.include_router(users.router)


@app.exception_handler(PollNotFoundException)
async def poll_not_found_handler(_: Request, exc: PollNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "poll_id": exc.poll_id
        }
    )
    
@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(_: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "user_id": exc.user_id
        }
    )

@app.get("/api/v1")
def read_root():
    return {"Hello": "World"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
