import uuid
from typing import Any, Optional
from pydantic import BaseModel
from langchain_core.messages import BaseMessage

from .content import ContentDTO

class Message(BaseMessage):
    pass

class MessageDTO(BaseModel):
    id: uuid.UUID
    content: ContentDTO
    create_time: Optional[float] = None
    update_time: Optional[float] = None
    metadata: Optional[Any] = None

    @property
    def message(self) -> BaseMessage:
        message = Message(type=self.content.content_type, content=self.content.parts)

        return message
