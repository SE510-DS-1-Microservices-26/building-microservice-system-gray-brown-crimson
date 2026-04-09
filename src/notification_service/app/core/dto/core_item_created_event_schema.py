from datetime import datetime
from pydantic import BaseModel


class CoreItemCreatedEventSchema(BaseModel):
    event_id: str
    occurred_at: datetime
    correlation_id: str
    core_item_id: str
    owner_user_id: str
    summary: str
