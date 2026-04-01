from uuid import UUID, uuid4
from dataclasses import dataclass, field
from datetime import datetime, UTC
from nanoid import generate

from .question import Question
from .vote import Vote
from .poll_status import PollStatus


def now_factory():
    return datetime.now(UTC)

def generate_short_id() -> str:
    return generate(size=8)    

@dataclass(kw_only=True)
class Poll:
    """Poll Domain Class"""
    id: UUID = field(default_factory=uuid4)
    short_id: str = field(default_factory=generate_short_id)
    name: str
    status: PollStatus = PollStatus.DRAFT
    user_id: UUID
    
    questions: list[Question] = field(default_factory=list)
    votes: list[Vote] = field(default_factory=list)
    created_at: datetime = field(default_factory=now_factory)
