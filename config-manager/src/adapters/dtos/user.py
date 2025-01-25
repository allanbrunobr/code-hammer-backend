from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class UserDTO(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr = Field(...)
    country: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=50)
    recovery_token: Optional[str] = Field(None, max_length=255)

    class Config:
        orm_mode = True


class UserCreateDTO(UserDTO):
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: str
    password: str
