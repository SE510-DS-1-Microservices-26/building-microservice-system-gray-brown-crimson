from uuid import UUID
from dataclasses import dataclass, field
from datetime import datetime, UTC

from .Question import Question
from .Vote import Vote
from .PollStatus import PollStatus


def now_factory():
    return datetime.now(UTC)


@dataclass(kw_only=True)
class Poll:
    """Poll Domain Class"""
    id: UUID
    name: str
    status: PollStatus = PollStatus.DRAFT
    user_id: UUID
    
    questions: list[Question] = field(default_factory=list)
    votes: list[Vote] = field(default_factory=list)
    created_at: datetime = field(default_factory=now_factory)
