import uuid

from app.core.domain import Poll, Question
from app.core.dto import CreatePollDto, PollDto, QuestionDto


class PollMapper:
    @staticmethod
    def to_domain(dto: CreatePollDto, user_id: str) -> Poll:
        domain_questions = [
            Question(
                id=uuid.uuid4(),
                question=q.question,
                options=q.options
            )
            for q in dto.questions
        ]
        
        return Poll(
            id=uuid.uuid4(),
            name=dto.name,
            user_id=uuid.UUID(user_id),
            questions=domain_questions
        )
        
    @staticmethod
    def to_dto(domain: Poll) -> PollDto:
        return PollDto(
            id=str(domain.id),
            name=domain.name,
            questions=[
                QuestionDto(
                    id=q.id,
                    question=q.question,
                    options=q.options
                )
                for q in domain.questions
            ]
        )
