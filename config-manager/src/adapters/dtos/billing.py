from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class BillingBaseDTO(BaseModel):
    amount: str = Field(..., max_length=100)
    currency: Optional[str] = Field(None, max_length=100)
    payment_date: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[str] = Field(None, max_length=100)
    payment_status: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    plan_id: Optional[str] = Field(None, max_length=100)
    user_id: Optional[UUID] = None  # Adicionando user_id

class BillingCreateDTO(BillingBaseDTO):
    pass

class BillingDTO(BillingBaseDTO):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
