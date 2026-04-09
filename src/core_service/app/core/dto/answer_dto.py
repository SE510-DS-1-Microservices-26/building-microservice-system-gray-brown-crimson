from uuid import UUID

from pydantic import BaseModel


class AnswerDto(BaseModel):
    question_id: UUID
    selected_option: str
