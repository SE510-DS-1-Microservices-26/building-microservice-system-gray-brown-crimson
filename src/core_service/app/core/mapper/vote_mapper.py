import uuid
from uuid import UUID

from src.core_service.app.core.domain import Vote
from src.core_service.app.core.domain.answer import Answer
from src.core_service.app.core.dto import CreateVoteDto, VoteDto
from src.core_service.app.core.dto.answer_dto import AnswerDto


class VoteMapper:
    @staticmethod
    def to_domain(dto: CreateVoteDto, poll_id: UUID, user_id: str) -> Vote:
        vote_id = uuid.uuid4()
        answers = [
            Answer(
                id=uuid.uuid4(),
                vote_id=vote_id,
                question_id=a.question_id,
                selected_option=a.selected_option,
            )
            for a in dto.answers
        ]
        return Vote(
            id=vote_id,
            poll_id=poll_id,
            user_id=uuid.UUID(user_id),
            answers=answers,
        )

    @staticmethod
    def to_dto(domain: Vote) -> VoteDto:
        return VoteDto(
            id=str(domain.id),
            poll_id=str(domain.poll_id),
            answers=[
                AnswerDto(
                    question_id=a.question_id,
                    selected_option=a.selected_option,
                )
                for a in domain.answers
            ],
            created_at=domain.created_at,
        )
