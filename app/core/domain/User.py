from uuid import UUID
from dataclasses import dataclass, field
from datetime import datetime, UTC


def now_factory():
    return datetime.now(UTC)


@dataclass
class User:
    """User Domain Class"""
    id: UUID
    firstname: str
    lastname: str
    email: str
    
    created_at: datetime = field(default_factory=now_factory)