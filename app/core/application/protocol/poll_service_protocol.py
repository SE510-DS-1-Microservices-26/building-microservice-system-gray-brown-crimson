from typing import Protocol

from app.core.dto import CreatePollDto, PollDto


class PollServiceProtocol(Protocol):     
    def get_poll(self, poll_id: str) -> PollDto:
        ...
    
    def add_new_poll(self, poll_id: str, dto: CreatePollDto) -> PollDto:
        ...

    def update_poll(self, poll_id: str, dto: CreatePollDto) -> PollDto:
        ...
        
    def delete_poll(self, poll_id: str) -> None:
        ...
