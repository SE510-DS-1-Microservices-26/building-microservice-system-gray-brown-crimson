import httpx

from src.shared.correlation import correlation_http_headers
from src.workflow_service.app.core.application.protocol import PollServiceProtocol
from src.workflow_service.app.core.exception import PollServiceUnavailableException
from src.workflow_service.app.core.infrastructure.client.http_retry import (
    request_with_retry,
)

_TIMEOUT = httpx.Timeout(5.0)


class PollClientService(PollServiceProtocol):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self._base_url = base_url
        self.client = client

    async def is_active(self, poll_id: str) -> bool:
        try:
            response = await request_with_retry(
                self.client,
                "GET",
                f"{self._base_url}/polls/{poll_id}",
                headers=correlation_http_headers(),
                timeout=_TIMEOUT,
            )
            response.raise_for_status()

            return response.json().get("status") == "active"
        except httpx.TimeoutException as exc:
            raise PollServiceUnavailableException(timeout=True) from exc
        except (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.RemoteProtocolError,
            httpx.HTTPStatusError,
        ) as exc:
            raise PollServiceUnavailableException(timeout=False) from exc
