from pydantic import BaseModel


class UserDto(BaseModel):
    id: str
    firstname: str
    lastname: str
    email: str
    