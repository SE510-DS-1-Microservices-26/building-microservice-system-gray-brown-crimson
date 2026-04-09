from datetime import datetime
from pydantic import BaseModel


class WorkflowDto(BaseModel):
    workflow_id: str
    type: str
    state: str
    poll_id: str | None
    user_id: str | None
    vote_id: str | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime
