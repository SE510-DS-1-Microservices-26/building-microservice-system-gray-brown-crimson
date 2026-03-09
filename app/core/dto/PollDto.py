from pydantic import BaseModel

from .QuestionDto import QuestionDto


class PollDto(BaseModel):
    id: str
    name: str
    questions: list[QuestionDto]
    