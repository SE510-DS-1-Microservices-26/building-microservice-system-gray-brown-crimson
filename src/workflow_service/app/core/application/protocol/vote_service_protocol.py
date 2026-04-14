from typing import Protocol


class VoteServiceProtocol(Protocol):
    async def has_user_voted(self, poll_id: str, user_id: str) -> bool: ...

    async def save_vote(
        self, poll_id: str, user_id: str, answers: list[dict]
    ) -> str: ...

    async def cancel_vote(self, vote_id: str, user_id: str) -> None: ...
