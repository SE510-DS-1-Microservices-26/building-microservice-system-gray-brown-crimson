from typing import Protocol

from app.core.domain import Poll
from app.core.dto import CreatePollDto, PollDto, UpdatePollStatusDto


class PollServiceProtocol(Protocol):
    def get_poll(self, poll_id: str, user_id: str) -> PollDto:
        ...

    def add_new_poll(self, user_id: str, dto: CreatePollDto) -> PollDto:
        ...

    def update_poll(self, poll_id: str, user_id: str, dto: CreatePollDto) -> PollDto:
        ...

    def update_poll_status(self, poll_id: str, user_id: str, dto: UpdatePollStatusDto) -> PollDto:
        ...

    def delete_poll(self, poll_id: str, user_id: str) -> None:
        ...

    def find_poll_for_user(self, poll_id: str, user_id: str) -> Poll:
        """Resolve poll UUID string to a Poll owned by the given user."""

    def find_poll(self, poll_id: str) -> Poll:
        """Resolve poll UUID string to a Poll regardless of ownership (e.g. for voting)."""

    def _is_poll_exists(self, poll_id: str) -> bool:
        ...
