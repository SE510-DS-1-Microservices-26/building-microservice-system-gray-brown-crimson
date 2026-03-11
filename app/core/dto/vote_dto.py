from datetime import datetime
from pydantic import BaseModel


class VoteDto(BaseModel):
    id: str
    poll_id: str
    
    created_at: datetime