import httpx

from src.core_service.app.core.application.protocol import UserServiceProtocol


class UserServiceClient(UserServiceProtocol):
    def __init__(self, base_url: str):
        self._base_url = base_url

    def user_exists(self, user_id: str) -> bool:
        response = httpx.get(f"{self._base_url}/{user_id}")
        return response.status_code == 200

    def get_user(self, user_id: str) -> dict:
        response = httpx.get(f"{self._base_url}/{user_id}")
        return response.json()