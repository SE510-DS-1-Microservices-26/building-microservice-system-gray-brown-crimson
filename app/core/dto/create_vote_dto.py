from pydantic import BaseModel


class CreateVoteDto(BaseModel):
    id: str
    poll_id: str