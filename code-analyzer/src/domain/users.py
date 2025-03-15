from pydantic import BaseModel
from typing import Optional
from .groups import UserGroup

class User(BaseModel):
    username: str
    email: str
    name: str
    password: str
    profile: UserGroup
    disabled: Optional[bool] = False

class LoginRequest(BaseModel):
    username: str
    password: str