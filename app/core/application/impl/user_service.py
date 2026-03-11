import logging
from app.core.application.protocol import UserServiceProtocol
from app.core.dto import CreateUserDto, UserDto
from app.core.domain import User
from app.core.mapper import UserMapper
from app.core.exception import UserNotFoundException


logger = logging.getLogger(__name__)

class UserService(UserServiceProtocol):
    def __init__(self):
        self.users = []
    
    def add_new_user(self, dto: CreateUserDto) -> UserDto:
        user = UserMapper.to_domain(dto)
        
        self.users.append(user)
        
        return UserMapper.to_dto(user)
    
    def get_user_info(self, user_id: str) -> UserDto:
        user = self._find_user_or_raise(user_id)
        return UserMapper.to_dto(user)
    
    def update_user(self, user_id: str, user_data: CreateUserDto) -> UserDto:
        user = self._find_user_or_raise(user_id)
        
        user.firstname = user_data.firstname
        user.lastname = user_data.lastname
        user.email = user_data.email
        
        return UserMapper.to_dto(user)
    
    def delete_user(self, user_id: str) -> None:
        self.users = [
            u for u in self.users
            if str(u.id) != user_id
        ]
        
    def _find_user_or_raise(self, user_id: str) -> User:
        user = next(
            (u for u in self.users if user_id == str(u.id)),
            None
        )
        
        if not user:
            logger.warning(f"User retrieval failed. ID {user_id} not found in data.")
            raise UserNotFoundException(user_id)
                
        return user
