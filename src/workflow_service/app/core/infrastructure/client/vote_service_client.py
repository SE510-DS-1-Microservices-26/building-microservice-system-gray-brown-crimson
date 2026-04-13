import httpx

from src.workflow_service.app.core.application.protocol import VoteServiceProtocol
from src.workflow_service.app.core.exception import VoteServiceUnavailableException

_TIMEOUT = httpx.Timeout(5.0)


class VoteClientService(VoteServiceProtocol):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self._base_url = base_url
        self.client = client

    async def has_user_voted(self, poll_id: str, user_id: str) -> bool:
        try:
            response = await self.client.get(
                f"{self._base_url}/votes/{poll_id}/user/{user_id}/",
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            return bool(response.json())
        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.HTTPStatusError,
        ) as exc:
            raise VoteServiceUnavailableException() from exc

    async def save_vote(self, poll_id: str, user_id: str, answers: list[dict]) -> str:
        try:
            response = await self.client.post(
                f"{self._base_url}/votes/{poll_id}",
                json={"answers": answers},
                headers={"x-user-id": user_id},
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            return data["id"]
        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.HTTPStatusError,
        ) as exc:
            raise VoteServiceUnavailableException() from exc

    async def cancel_vote(self, vote_id: str, user_id: str) -> None:
        try:
            response = await self.client.delete(
                f"{self._base_url}/votes/vote/{vote_id}",
                headers={"x-user-id": user_id},
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.HTTPStatusError,
        ) as exc:
            raise VoteServiceUnavailableException() from exc
