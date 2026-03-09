from typing import Protocol


class UserServiceProtocol(Protocol):
    def add_new_user(self, user_data: dict) -> dict:
        ...