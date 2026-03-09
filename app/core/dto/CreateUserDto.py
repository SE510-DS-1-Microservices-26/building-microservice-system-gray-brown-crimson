from pydantic import BaseModel


class CreateUserDto(BaseModel):
    firstname: str
    lastname: str
    email: str
    