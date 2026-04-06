from datetime import datetime
from pydantic import BaseModel

from .answer_dto import AnswerDto


class VoteDto(BaseModel):
    id: str
    poll_id: str
    answers: list[AnswerDto]
    created_at: datetime
