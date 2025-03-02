from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserDTO(BaseModel):
    id: Optional[UUID] = None
    name: str = Field(..., max_length=100)
    email: EmailStr = Field(...)
    country: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=50)
    recovery_token: Optional[str] = Field(None, max_length=255)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserCreateDTO(BaseModel):
    email: EmailStr = Field(...)
    name: Optional[str] = Field(None, max_length=100)
    firebase_uid: Optional[str] = Field(None, max_length=255)  # Add Firebase UID


class UserUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = Field(None)
    country: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=50)


class LoginRequest(BaseModel):
    email: str
    password: str

class UserIdDTO(BaseModel):
    userId: UUID


class UserEmailQueryDTO(BaseModel):
    email: str
