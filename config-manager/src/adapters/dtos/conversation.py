import uuid
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from .message import MessageDTO
from .document import DocumentDTO

class ConversationDTO(BaseModel):

    message: str
