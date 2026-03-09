from app.core.application.user_service_protocol import UserServiceProtocol


class UserService(UserServiceProtocol):
    def __init__(self):
        pass
    
    def add_new_user(self, user_data: dict) -> dict:
        return {}
    
    
def get_user_service() -> UserServiceProtocol:
    return UserService()
