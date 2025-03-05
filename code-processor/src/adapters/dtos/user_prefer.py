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
    post_comment: Optional[bool] = True
    files_to_analyze: Optional[List[str]] = None
    files_count: Optional[int] = 0
