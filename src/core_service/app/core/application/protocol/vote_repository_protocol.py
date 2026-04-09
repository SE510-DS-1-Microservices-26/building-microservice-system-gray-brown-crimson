from typing import Protocol
from uuid import UUID

from src.core_service.app.core.domain.vote import Vote


class VoteRepositoryProtocol(Protocol):
    def save(self, vote: Vote) -> Vote: ...

    def find_by_poll_and_user(self, poll_id: UUID, user_id: UUID) -> list[Vote]: ...

    def check_user_voted(self, poll_id: UUID, user_id: UUID) -> bool: ...
