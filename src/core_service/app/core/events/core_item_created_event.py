import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class CoreItemCreatedEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    core_item_id: str
    owner_user_id: str
    summary: str
