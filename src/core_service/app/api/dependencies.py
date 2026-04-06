from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from src.core_service.app.core.application import PollService, VoteService
from src.core_service.app.core.infrastructure import SessionLocal, UserServiceClient
from src.core_service.app.core.infrastructure.repository import (
    OutboxRepository,
    PollRepository,
    VoteRepository,
)
from src.core_service.app.shared import settings


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_service_client() -> UserServiceClient:
    return UserServiceClient(settings.users_service_url)


def get_poll_service(
    db: Session = Depends(get_db),
    user_client: UserServiceClient = Depends(get_user_service_client),
) -> PollService:
    return PollService(PollRepository(db), user_client, OutboxRepository(db))


def get_vote_service(
    poll_service: PollService = Depends(get_poll_service),
    db: Session = Depends(get_db),
    user_client: UserServiceClient = Depends(get_user_service_client),
) -> VoteService:
    return VoteService(poll_service, VoteRepository(db), user_client)


def get_current_user_id(
    x_user_id: str = Header(default="00000000-0000-0000-0000-000000000001"),
) -> str:
    return x_user_id
