from pydantic import BaseModel, UUID4


class AnswerWorkflowDto(BaseModel):
    question_id: UUID4
    selected_option: str


class StartVoteWorkflowDto(BaseModel):
    user_id: UUID4
    poll_id: UUID4
    answers: list[AnswerWorkflowDto]
