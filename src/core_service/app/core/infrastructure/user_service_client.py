import httpx

from src.core_service.app.core.application.protocol import UserServiceProtocol
from src.core_service.app.core.exception import UsersServiceUnavailableException

_TIMEOUT = httpx.Timeout(5.0)


class UserServiceClient(UserServiceProtocol):
    def __init__(self, base_url: str):
        self._base_url = base_url

    def user_exists(self, user_id: str) -> bool:
        try:
            response = httpx.get(f"{self._base_url}/{user_id}", timeout=_TIMEOUT)
            return response.status_code == 200
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            raise UsersServiceUnavailableException() from exc

    def get_user(self, user_id: str) -> dict:
        try:
            response = httpx.get(f"{self._base_url}/{user_id}", timeout=_TIMEOUT)
            return response.json()
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            raise UsersServiceUnavailableException() from exc
