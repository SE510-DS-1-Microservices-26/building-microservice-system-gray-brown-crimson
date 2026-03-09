from uuid import UUID
from dataclasses import dataclass
from datetime import datetime, UTC


def now_factory():
    return datetime.now(UTC)


@dataclass
class Question:
    """Question Domain Class"""
    id: UUID
    question: str
    options: list[str]
