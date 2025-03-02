from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import json

from .repository import RepositoryDTO

class MessageDTO(BaseModel):
    language: str
    prompt: str
    name: str
    code: str
    email: EmailStr
    token: str
    repository: RepositoryDTO
    
    def __str__(self) -> str:
        """Converte o objeto para JSON string para publicação no PubSub"""
        return json.dumps(self.dict())
