from pydantic import BaseModel

from src.core_service.app.core.domain.poll_status import PollStatus
from .question_dto import QuestionDto


class PollDto(BaseModel):
    id: str
    name: str
    status: PollStatus
    questions: list[QuestionDto]
