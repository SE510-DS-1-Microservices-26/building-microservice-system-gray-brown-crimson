from pydantic import BaseModel


class UserDto(BaseModel):
    id: str
    username: str
    firstname: str
    lastname: str
    email: str
