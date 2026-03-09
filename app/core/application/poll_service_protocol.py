from typing import Protocol

from app.core.dto.PollDto import PollDto
from app.core.dto.CreatePollDto import CreatePollDto


class PollServiceProtocol(Protocol):     
    def get_poll(self, poll_id: str) -> PollDto:
        ...
    
    def add_new_poll(self, user_id: str, dto: CreatePollDto) -> PollDto:
        ...
