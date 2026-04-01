from typing import Protocol

from app.core.dto import CreateVoteDto, VoteDto


class VoteServiceProtocol(Protocol):     
    def get_votes(self, poll_id: str, user_id: str) -> list[VoteDto]:
        ...
        
    def add_vote(self, poll_id: str, user_id: str, dto: CreateVoteDto) -> VoteDto:
        ...
