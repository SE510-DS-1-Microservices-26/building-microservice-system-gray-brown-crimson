from uuid import UUID
from dataclasses import dataclass, field
from datetime import datetime, UTC


def now_factory():
    return datetime.now(UTC)


@dataclass
class User:
    """User Domain Class"""

    id: UUID
    username: str
    firstname: str
    lastname: str
    email: str

    created_at: datetime = field(default_factory=now_factory)

    def __post_init__(self) -> None:
        if not self.username or not self.username.strip():
            raise ValueError("Username cannot be empty.")
        if not self.email or "@" not in self.email:
            raise ValueError("Email must be valid.")
