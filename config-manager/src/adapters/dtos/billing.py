from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class BillingDTO(BaseModel):
    amount: str = Field(..., max_length=100)
    currency: Optional[str] = Field(None, max_length=100)
    payment_date: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[str] = Field(None, max_length=100)
    payment_status: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    plan_id: Optional[str] = Field(None, max_length=100)

class BillingCreateDTO(BillingDTO):
    pass

class BillingDTO(BillingDTO):
    uuid: UUID
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True
