from uuid import UUID
from dataclasses import dataclass, field
from datetime import datetime, UTC

def now_factory():
    return datetime.now(UTC)


@dataclass
class Vote:
    id: UUID
    name: str
    created_at: datetime = field(default_factory=now_factory)
