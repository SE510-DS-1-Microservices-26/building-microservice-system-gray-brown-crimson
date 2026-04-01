from pydantic import BaseModel, Field, EmailStr


class CreateUserDto(BaseModel):
    username: str = Field(min_length=3, description="Must be at least 3 characters.")
    firstname: str = Field(min_length=2, description="Must be at least 2 characters.")
    lastname: str = Field(min_length=2, description="Must be at least 2 characters.")
    email: EmailStr
    