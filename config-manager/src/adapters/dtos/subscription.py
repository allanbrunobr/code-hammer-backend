from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal


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


class PlanDTO(BaseModel):
    id: UUID
    name: str
    file_limit: Optional[int]
    status: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True


class PeriodDTO(BaseModel):
    id: UUID
    name: str
    months: int
    discount_percentage: Optional[int] = 0

    class Config:
        orm_mode = True


class PlanPeriodDTO(BaseModel):
    id: UUID
    plan_id: UUID
    period_id: UUID
    price: Decimal
    currency: str

    class Config:
        orm_mode = True


class SubscriptionDTO(SubscriptionBaseDTO):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    plan: Optional[PlanDTO]

    class Config:
        orm_mode = True


class SubscriptionFullDTO(SubscriptionDTO):
    """DTO estendido incluindo todos os detalhes do plano e período"""
    plan: PlanDTO
    price: Optional[Decimal]
    currency: Optional[str] = "BRL"

    class Config:
        orm_mode = True


class SubscriptionResponseDTO(BaseModel):
    """DTO para resposta da API formatado para o frontend"""
    id: str
    status: str
    plan: str
    planId: str
    startDate: Optional[str]
    endDate: Optional[str]
    remainingFileQuota: Optional[int]
    autoRenew: bool
    description: Optional[str]
    price: float
