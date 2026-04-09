from uuid import UUID
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification:
    event_id: UUID
    occurred_at: datetime
    correlation_id: UUID
    core_item_id: UUID
    owner_user_id: UUID
    summary: str

    def __post_init__(self) -> None:
        if not self.summary or not self.summary.strip():
            raise ValueError("Summary cannot be empty.")
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware.")