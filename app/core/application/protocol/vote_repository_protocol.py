from typing import Protocol
from uuid import UUID

from app.core.domain.vote import Vote


class VoteRepositoryProtocol(Protocol):
    def save(self, vote: Vote) -> Vote:
        ...

    def find_by_poll_and_user(self, poll_id: UUID, user_id: UUID) -> list[Vote]:
        ...
