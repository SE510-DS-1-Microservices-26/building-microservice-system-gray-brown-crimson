from typing import Protocol
from uuid import UUID

from src.users_service.app.core.domain import User


class UserRepositoryProtocol(Protocol):
    def find_by_id(self, user_id: UUID) -> User | None:
        ...

    def save(self, user: User) -> User:
        ...

    def delete(self, user_id: UUID) -> None:
        ...
