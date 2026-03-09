from pydantic import BaseModel


class CreateQuestionDto(BaseModel):
    question: str
    options: list[str]
