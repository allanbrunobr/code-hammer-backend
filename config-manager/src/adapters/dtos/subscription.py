from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class SubscriptionBaseDTO(BaseModel):
    status: str = Field(..., max_length=100)
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    remaining_file_quota: Optional[int]
    auto_renew: Optional[bool] = False
    plan_id: UUID
    user_id: UUID


class SubscriptionCreateDTO(SubscriptionBaseDTO):
    pass


class SubscriptionDTO(SubscriptionBaseDTO):
    uuid: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
