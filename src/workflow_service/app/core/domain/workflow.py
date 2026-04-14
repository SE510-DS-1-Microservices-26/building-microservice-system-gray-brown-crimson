import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum


class WorkflowType(str, Enum):
    VOTE = "vote"


class WorkflowState(str, Enum):
    PENDING = "PENDING"
    POLL_LOCKED = "POLL_LOCKED"
    VOTE_SAVED = "VOTE_SAVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def now_factory():
    return datetime.now(UTC)


@dataclass
class WorkflowInstance:
    type: WorkflowType
    state: WorkflowState = WorkflowState.PENDING
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=now_factory)
    updated_at: datetime = field(default_factory=now_factory)
    last_error: str | None = None

    poll_id: str | None = None
    user_id: str | None = None
    vote_id: str | None = None
