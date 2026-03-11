from uuid import UUID
from dataclasses import dataclass, field
from datetime import datetime, UTC

def now_factory():
    return datetime.now(UTC)


@dataclass
class Vote:
    id: UUID
    poll_id: UUID
    user_id: UUID
        
    created_at: datetime = field(default_factory=now_factory)
