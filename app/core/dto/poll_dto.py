from pydantic import BaseModel

from app.core.domain.poll_status import PollStatus
from .question_dto import QuestionDto


class PollDto(BaseModel):
    id: str
    name: str
    status: PollStatus
    questions: list[QuestionDto]
