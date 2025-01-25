from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class ProcessRequestDTO(BaseModel):
    code: str = Field(...)
    email: EmailStr = Field(...)
    token: Optional[str] = Field(None, max_length=50)
    url_pr: Optional[str] = Field(None)

    class Config:
        orm_mode = True

