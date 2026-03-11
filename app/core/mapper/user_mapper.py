import uuid

from app.core.domain import User
from app.core.dto import CreateUserDto, UserDto


class UserMapper:
    @staticmethod
    def to_domain(dto: CreateUserDto) -> User:
        return User(
            id=uuid.uuid4(),
            username=dto.username,
            firstname=dto.firstname,
            lastname=dto.lastname,
            email=dto.email
        )
        
    @staticmethod
    def to_dto(domain: User) -> UserDto:
        return UserDto(
            id=str(domain.id),
            username=domain.username,
            firstname=domain.firstname,
            lastname=domain.lastname,
            email=domain.email
        )
