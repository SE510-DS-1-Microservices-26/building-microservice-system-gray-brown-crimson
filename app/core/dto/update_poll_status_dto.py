from pydantic import BaseModel

from app.core.domain.poll_status import PollStatus


class UpdatePollStatusDto(BaseModel):
    status: PollStatus
