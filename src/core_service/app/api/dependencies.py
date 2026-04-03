from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from src.core_service.app.core.application import PollService, VoteService
from src.core_service.app.core.infrastructure import SessionLocal
from src.core_service.app.core.infrastructure.repository import PollRepository, VoteRepository


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_poll_service(db: Session = Depends(get_db)) -> PollService:
    return PollService(PollRepository(db))


def get_vote_service(
    poll_service: PollService = Depends(get_poll_service),
    db: Session = Depends(get_db),
) -> VoteService:
    return VoteService(poll_service, VoteRepository(db))


def get_current_user_id(x_user_id: str = Header(default="00000000-0000-0000-0000-000000000001")) -> str:
    return x_user_id
