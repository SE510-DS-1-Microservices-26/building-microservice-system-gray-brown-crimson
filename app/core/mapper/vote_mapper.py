import uuid

from app.core.domain import Vote
from app.core.dto import CreateVoteDto, VoteDto


class VoteMapper:
    @staticmethod
    def to_domain(dto: CreateVoteDto, user_id: str) -> Vote:
        return Vote(
            id=uuid.uuid4(),
            poll_id=uuid.UUID(dto.poll_id),
            user_id=uuid.UUID(user_id)
        )
        
    @staticmethod
    def to_dto(domain: Vote) -> VoteDto:
        return VoteDto(
            id=str(domain.id),
            poll_id=str(domain.poll_id),
            created_at=domain.created_at
        )
