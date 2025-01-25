from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class IntegrationBaseDTO(BaseModel):
    name: str = Field(..., max_length=100)
    api_key: Optional[str] = Field(None, max_length=100)
    repository: Optional[str] = Field(None, max_length=100)
    repository_user: Optional[str] = Field(None, max_length=100)
    repository_token: Optional[str] = Field(None, max_length=100)
    repository_url: Optional[str] = Field(None, max_length=100)
    analyze_types: Optional[str] = Field(None, max_length=100)
    quality_level: Optional[str] = Field(None, max_length=100)
    user_id: Optional[str] = Field(None, max_length=100)


class IntegrationCreateDTO(IntegrationBaseDTO):
    pass


class IntegrationDTO(IntegrationBaseDTO):
    uuid: UUID
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True
