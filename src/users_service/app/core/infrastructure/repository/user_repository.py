from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from src.users_service.app.core.domain import User
from src.users_service.app.core.infrastructure.models import UserModel


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, user_id: UUID) -> User | None:
        row = self._session.get(UserModel, user_id)
        return self._to_domain(row) if row else None

    def save(self, user: User) -> User:
        existing = self._session.get(UserModel, user.id)
        if existing:
            existing.username = user.username
            existing.firstname = user.firstname
            existing.lastname = user.lastname
            existing.email = user.email
        else:
            row = UserModel(
                id=user.id,
                username=user.username,
                firstname=user.firstname,
                lastname=user.lastname,
                email=user.email,
                created_at=user.created_at.isoformat(),
            )
            self._session.add(row)
        self._session.commit()
        return user

    def delete(self, user_id: UUID) -> None:
        row = self._session.get(UserModel, user_id)
        if row:
            self._session.delete(row)
            self._session.commit()

    @staticmethod
    def _to_domain(row: UserModel) -> User:
        return User(
            id=row.id,
            username=row.username,
            firstname=row.firstname,
            lastname=row.lastname,
            email=row.email,
            created_at=datetime.fromisoformat(row.created_at),
        )
