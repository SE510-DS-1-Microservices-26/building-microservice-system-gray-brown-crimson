from typing import Protocol

from app.core.dto import VoteDto

class VoteServiceProtocol(Protocol):     
    def get_votes(self, poll_id: str) -> list[VoteDto]:
        ...
