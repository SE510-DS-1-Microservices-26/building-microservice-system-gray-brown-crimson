import httpx

from src.workflow_service.app.core.application.protocol import PollServiceProtocol
from src.workflow_service.app.core.exception import PollServiceUnavailableException

_TIMEOUT = httpx.Timeout(5.0)


class PollService(PollServiceProtocol):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self._base_url = base_url
        self.client = client

    async def is_active(self, poll_id: str) -> bool:
        try:
            response = await self.client.get(
                f"{self._base_url}/{poll_id}", timeout=_TIMEOUT
            )
            response.raise_for_status()

            return response.json().get("status") == "active"
        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.HTTPStatusError,
        ) as exc:
            raise PollServiceUnavailableException() from exc
