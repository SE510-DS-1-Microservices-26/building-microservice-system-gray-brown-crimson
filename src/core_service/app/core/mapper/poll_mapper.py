import uuid

from src.core_service.app.core.domain import Poll, Question
from src.core_service.app.core.dto import CreatePollDto, PollDto, QuestionDto


class PollMapper:
    @staticmethod
    def to_domain(dto: CreatePollDto, user_id: str) -> Poll:
        poll_id = uuid.uuid4()
        domain_questions = [
            Question(
                id=uuid.uuid4(), poll_id=poll_id, question=q.question, options=q.options
            )
            for q in dto.questions
        ]

        return Poll(
            id=poll_id,
            name=dto.name,
            user_id=uuid.UUID(user_id),
            questions=domain_questions,
        )

    @staticmethod
    def to_dto(domain: Poll) -> PollDto:
        return PollDto(
            id=str(domain.id),
            name=domain.name,
            status=domain.status,
            questions=[
                QuestionDto(id=q.id, question=q.question, options=q.options)
                for q in domain.questions
            ],
        )
