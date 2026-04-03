from uuid import UUID

from pydantic import BaseModel


class CreateAnswerDto(BaseModel):
    question_id: UUID
    selected_option: str
