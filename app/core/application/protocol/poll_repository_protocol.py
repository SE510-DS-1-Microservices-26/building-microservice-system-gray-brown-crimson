from typing import Protocol
from uuid import UUID

from app.core.domain import Poll


class PollRepositoryProtocol(Protocol):
    def find_by_short_id(self, short_id: str, user_id: UUID) -> Poll | None:
        ...

    def save(self, poll: Poll) -> Poll:
        ...

    def delete(self, short_id: str, user_id: UUID) -> None:
        ...

    def exists_by_short_id(self, short_id: str) -> bool:
        ...
