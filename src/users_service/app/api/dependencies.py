from typing import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from src.users_service.app.core.infrastructure import SessionLocal
from src.users_service.app.core.infrastructure.repository import UserRepository
from src.users_service.app.core.application import UserService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


def get_current_user_id(x_user_id: str = Header(default="00000000-0000-0000-0000-000000000001")) -> str:
    return x_user_id
