import logging
import uuid

from src.users_service.app.core.application.protocol import UserRepositoryProtocol
from src.users_service.app.core.dto import CreateUserDto, UpdateUserDto, UserDto
from src.users_service.app.core.domain import User
from src.users_service.app.core.mapper import UserMapper
from src.users_service.app.core.exception import UserNotFoundException


logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, repository: UserRepositoryProtocol):
        self._repository = repository

    def add_new_user(self, dto: CreateUserDto) -> UserDto:
        user = UserMapper.to_domain(dto)
        self._repository.save(user)
        return UserMapper.to_dto(user)

    def get_user_info(self, user_id: str) -> UserDto:
        user = self._find_user_or_raise(user_id)
        return UserMapper.to_dto(user)

    def update_user(self, user_id: str, user_data: UpdateUserDto) -> UserDto:
        user = self._find_user_or_raise(user_id)
        user.firstname = user_data.firstname
        user.lastname = user_data.lastname
        user.email = user_data.email
        self._repository.save(user)
        return UserMapper.to_dto(user)

    def delete_user(self, user_id: str) -> None:
        self._repository.delete(uuid.UUID(user_id))

    def _find_user_or_raise(self, user_id: str) -> User:
        user = self._repository.find_by_id(uuid.UUID(user_id))
        if not user:
            logger.warning(f"User retrieval failed. ID {user_id} not found in data.")
            raise UserNotFoundException(user_id)
        return user
