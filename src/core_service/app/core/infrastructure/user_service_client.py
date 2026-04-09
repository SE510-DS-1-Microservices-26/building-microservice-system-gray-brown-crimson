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
            if response.status_code == 200:
                return True
            if response.status_code == 404:
                return False
            raise UsersServiceUnavailableException()
        except httpx.RequestError as exc:
            raise UsersServiceUnavailableException() from exc

    def get_user(self, user_id: str) -> dict:
        try:
            response = httpx.get(f"{self._base_url}/{user_id}", timeout=_TIMEOUT)
            return response.json()
        except httpx.RequestError as exc:
            raise UsersServiceUnavailableException() from exc
