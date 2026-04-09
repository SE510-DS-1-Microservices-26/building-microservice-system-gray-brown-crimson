from uuid import UUID
from dataclasses import dataclass
from datetime import datetime, UTC


def now_factory():
    return datetime.now(UTC)


@dataclass
class Question:
    """Question Domain Class"""

    id: UUID
    poll_id: UUID
    question: str
    options: list[str]

    def __post_init__(self) -> None:
        if not self.question or not self.question.strip():
            raise ValueError("Question text cannot be empty.")
        if len(self.options) < 2:
            raise ValueError("A question must have at least 2 options.")
