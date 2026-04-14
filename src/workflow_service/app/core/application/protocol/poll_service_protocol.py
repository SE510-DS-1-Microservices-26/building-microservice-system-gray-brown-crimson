from typing import Protocol


class PollServiceProtocol(Protocol):
    async def is_active(self, poll_id: str) -> bool: ...
