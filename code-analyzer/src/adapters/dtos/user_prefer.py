from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

from .repository import RepositoryDTO


class UserPreferDTO(BaseModel):
    language: str = Field(...)
    prompt: str = Field(...)
    name: str
    code: str
    email: EmailStr
    token: str = Field(...)
    repository: RepositoryDTO
    analyze_full_project: Optional[bool] = False
    modified_files: Optional[List[str]] = None