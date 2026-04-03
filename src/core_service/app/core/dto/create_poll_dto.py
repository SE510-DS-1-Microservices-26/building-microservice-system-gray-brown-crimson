from pydantic import BaseModel, Field

from .create_question_dto import CreateQuestionDto

class CreatePollDto(BaseModel):
    name: str = Field(min_length=3, description="Must be at least 3 characters.")
    questions: list[CreateQuestionDto]
    