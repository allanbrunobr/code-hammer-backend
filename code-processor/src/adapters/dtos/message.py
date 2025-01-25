from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class MessageDTO(BaseModel):
    code: str = Field(...)


