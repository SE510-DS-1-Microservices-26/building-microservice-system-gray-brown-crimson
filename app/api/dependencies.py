from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.application.protocol import PollServiceProtocol, VoteServiceProtocol, UserServiceProtocol
from app.core.application.impl import PollService, VoteService, UserService
from app.core.infrastructure import SessionLocal, PollRepository, UserRepository, VoteRepository


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_poll_service(db: Session = Depends(get_db)) -> PollServiceProtocol:
    return PollService(PollRepository(db))


def get_vote_service(
    poll_service: PollServiceProtocol = Depends(get_poll_service),
    db: Session = Depends(get_db),
) -> VoteServiceProtocol:
    return VoteService(poll_service, VoteRepository(db))


def get_user_service(db: Session = Depends(get_db)) -> UserServiceProtocol:
    return UserService(UserRepository(db))


def get_current_user_id(x_user_id: str = Header(default="00000000-0000-0000-0000-000000000001")) -> str:
    return x_user_id
