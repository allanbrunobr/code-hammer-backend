# adapters/dtos/plan_dto.py
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class PlanBaseDTO(BaseModel):
    name: str = Field(..., max_length=100)
    file_limit: Optional[int]
    status: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    # permissions: Optional[List[str]]


class PlanCreateDTO(PlanBaseDTO):
    pass


class PlanDTO(PlanBaseDTO):
    uuid: UUID
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True
