from pydantic import BaseModel, EmailStr, Field

from .repository import RepositoryDTO

class UserPreferDTO(BaseModel):
    language: str = Field(...)
    prompt: str = Field(...)
    name: str
    code: str
    email: EmailStr
    token: str = Field(...)
    repository: RepositoryDTO
