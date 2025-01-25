from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class PubSubDTO(BaseModel):
    project_id: str = Field(...)
    topic_id: str = Field(...)
    subscription_id: str = Field(...)
