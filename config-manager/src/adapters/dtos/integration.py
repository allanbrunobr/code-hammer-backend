from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class IntegrationBaseDTO(BaseModel):
    name: str = Field(..., max_length=100)
    api_key: Optional[str] = Field(None, max_length=100)
    repository: Optional[str] = Field(None, max_length=100)
    repository_user: Optional[str] = Field(None, max_length=100)
    repository_token: Optional[str] = Field(None, max_length=100)
    repository_url: Optional[str] = Field(None, max_length=100)
    analyze_types: Optional[str] = Field(None, max_length=100)
    quality_level: Optional[str] = Field(None, max_length=100)
    user_id: Optional[UUID] = Field(None)


class IntegrationCreateDTO(IntegrationBaseDTO):
    pass


class IntegrationDTO(IntegrationBaseDTO):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
