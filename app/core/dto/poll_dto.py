from pydantic import BaseModel

from .question_dto import QuestionDto


class PollDto(BaseModel):
    id: str
    name: str
    questions: list[QuestionDto]
    