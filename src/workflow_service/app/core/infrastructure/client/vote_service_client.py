import httpx

from src.shared.correlation import correlation_http_headers
from src.workflow_service.app.core.application.protocol import VoteServiceProtocol
from src.workflow_service.app.core.exception import VoteServiceUnavailableException
from src.workflow_service.app.core.infrastructure.client.http_retry import (
    request_with_retry,
)

_TIMEOUT = httpx.Timeout(5.0)


class VoteClientService(VoteServiceProtocol):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self._base_url = base_url
        self.client = client

    def _user_headers(self, user_id: str) -> dict[str, str]:
        h = correlation_http_headers()
        h["x-user-id"] = user_id
        return h

    async def has_user_voted(self, poll_id: str, user_id: str) -> bool:
        try:
            response = await request_with_retry(
                self.client,
                "GET",
                f"{self._base_url}/votes/{poll_id}/user/{user_id}/",
                headers=correlation_http_headers(),
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            return bool(response.json())
        except httpx.TimeoutException as exc:
            raise VoteServiceUnavailableException(timeout=True) from exc
        except (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.RemoteProtocolError,
            httpx.HTTPStatusError,
        ) as exc:
            raise VoteServiceUnavailableException(timeout=False) from exc

    async def save_vote(self, poll_id: str, user_id: str, answers: list[dict]) -> str:
        try:
            response = await request_with_retry(
                self.client,
                "POST",
                f"{self._base_url}/votes/{poll_id}",
                json={"answers": answers},
                headers=self._user_headers(user_id),
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            return data["id"]
        except httpx.TimeoutException as exc:
            raise VoteServiceUnavailableException(timeout=True) from exc
        except (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.RemoteProtocolError,
            httpx.HTTPStatusError,
        ) as exc:
            raise VoteServiceUnavailableException(timeout=False) from exc

    async def cancel_vote(self, vote_id: str, user_id: str) -> None:
        try:
            response = await request_with_retry(
                self.client,
                "DELETE",
                f"{self._base_url}/votes/vote/{vote_id}",
                headers=self._user_headers(user_id),
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise VoteServiceUnavailableException(timeout=True) from exc
        except (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.RemoteProtocolError,
            httpx.HTTPStatusError,
        ) as exc:
            raise VoteServiceUnavailableException(timeout=False) from exc
