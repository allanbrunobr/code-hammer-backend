from typing import List, Any
from pydantic import BaseModel

class ContentDTO(BaseModel):
    content_type: str
    parts: str|List[Any] = None
