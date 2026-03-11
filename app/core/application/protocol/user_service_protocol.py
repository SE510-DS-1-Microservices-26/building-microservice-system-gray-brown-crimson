from typing import Protocol

from app.core.dto import CreateUserDto, UserDto

class UserServiceProtocol(Protocol):
    def add_new_user(self, user_data: CreateUserDto) -> UserDto:
        ...
        
    def get_user_info(self, user_id: str) -> UserDto:
        ...
        
    def update_user(self, user_id: str, user_data: CreateUserDto) -> UserDto:
        ...
        
    def delete_user(self, user_id: str) -> None:
        ...