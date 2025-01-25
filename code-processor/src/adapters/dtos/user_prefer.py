from pydantic import BaseModel, EmailStr, Field

from .repository import RepositoryDTO

class UserPreferDTO(BaseModel):
    language: str = Field(...)
    prompt: str = Field(...)
    name: str
    email: EmailStr
    repository: RepositoryDTO




