from uuid import uuid4, UUID
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Answer:
    id: UUID = field(default_factory=uuid4)
    vote_id: UUID
    question_id: UUID
    selected_option: str
