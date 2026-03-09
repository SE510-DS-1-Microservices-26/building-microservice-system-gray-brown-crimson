from pydantic import BaseModel

from .CreateQuestionDto import CreateQuestionDto

class CreatePollDto(BaseModel):
    name: str
    questions: list[CreateQuestionDto]
    