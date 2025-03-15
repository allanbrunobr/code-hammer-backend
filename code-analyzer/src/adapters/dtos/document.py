from typing import Any, Optional
from pydantic import BaseModel

from .content import ContentDTO

class DocumentDTO(BaseModel):
    content: ContentDTO
    metadata: Optional[Any] = None
