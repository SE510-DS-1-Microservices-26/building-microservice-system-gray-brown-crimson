from pydantic import BaseModel

from .create_answer_dto import CreateAnswerDto


class CreateVoteDto(BaseModel):
    answers: list[CreateAnswerDto]
