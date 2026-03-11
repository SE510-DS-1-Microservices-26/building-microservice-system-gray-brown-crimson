from uuid import UUID
from pydantic import BaseModel


class QuestionDto(BaseModel):
    id: UUID
    question: str
    options: list[str]
