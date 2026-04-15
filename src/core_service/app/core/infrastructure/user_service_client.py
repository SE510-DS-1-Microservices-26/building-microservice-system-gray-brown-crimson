import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.core_service.app.core.application.protocol import UserServiceProtocol
from src.core_service.app.core.exception import (
    UsersServiceTimeoutException,
    UsersServiceUnavailableException,
)
from src.shared.correlation import correlation_http_headers

_TIMEOUT = httpx.Timeout(5.0)


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.3, min=0.3, max=2.0),
    retry=retry_if_exception_type(
        (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.RemoteProtocolError,
            httpx.TimeoutException,
        )
    ),
)
def _http_get(url: str, headers: dict[str, str]) -> httpx.Response:
    return httpx.get(url, headers=headers, timeout=_TIMEOUT)


class UserServiceClient(UserServiceProtocol):
    def __init__(self, base_url: str):
        self._base_url = base_url

    def user_exists(self, user_id: str) -> bool:
        try:
            response = _http_get(
                f"{self._base_url}/{user_id}", correlation_http_headers()
            )
            return response.status_code == 200
        except httpx.TimeoutException as exc:
            raise UsersServiceTimeoutException() from exc
        except (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.RemoteProtocolError,
        ) as exc:
            raise UsersServiceUnavailableException() from exc

    def get_user(self, user_id: str) -> dict:
        try:
            response = _http_get(
                f"{self._base_url}/{user_id}", correlation_http_headers()
            )
            return response.json()
        except httpx.TimeoutException as exc:
            raise UsersServiceTimeoutException() from exc
        except (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.RemoteProtocolError,
        ) as exc:
            raise UsersServiceUnavailableException() from exc
