from uuid import UUID, uuid4
from dataclasses import dataclass, field
from datetime import datetime, UTC
from nanoid import generate

from .question import Question
from .vote import Vote
from .poll_status import PollStatus


_VALID_TRANSITIONS: dict[PollStatus, set[PollStatus]] = {
    PollStatus.DRAFT: {PollStatus.ACTIVE},
    PollStatus.ACTIVE: {PollStatus.COMPLETED},
    PollStatus.COMPLETED: set(),
}


def now_factory():
    return datetime.now(UTC)

def generate_short_id() -> str:
    return generate(size=8)

@dataclass(kw_only=True)
class Poll:
    id: UUID = field(default_factory=uuid4)
    short_id: str = field(default_factory=generate_short_id)
    name: str
    status: PollStatus = PollStatus.DRAFT
    user_id: UUID

    questions: list[Question] = field(default_factory=list)
    votes: list[Vote] = field(default_factory=list)
    created_at: datetime = field(default_factory=now_factory)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Poll name cannot be empty.")

    def change_status(self, new_status: PollStatus) -> None:
        if new_status not in _VALID_TRANSITIONS[self.status]:
            raise ValueError(
                f"Cannot transition poll from {self.status} to {new_status}."
            )
        self.status = new_status

    def add_question(self, question: Question) -> None:
        if self.status != PollStatus.DRAFT:
            raise ValueError("Questions can only be added to a poll in DRAFT status.")
        self.questions.append(question)
