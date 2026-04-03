from pydantic import BaseModel

from src.core_service.app.core.domain.poll_status import PollStatus


class UpdatePollStatusDto(BaseModel):
    status: PollStatus
