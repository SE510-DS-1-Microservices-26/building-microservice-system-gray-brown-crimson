from typing import Protocol


class UserServiceProtocol(Protocol):
    def user_exists(self, user_id: str) -> bool: ...

    def get_user(self, user_id: str) -> dict: ...
