from pydantic import BaseModel, Field, EmailStr


class UpdateUserDto(BaseModel):
    firstname: str = Field(min_length=2, description="Must be at least 2 characters.")
    lastname: str = Field(min_length=2, description="Must be at least 2 characters.")
    email: EmailStr
