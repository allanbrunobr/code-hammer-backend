# routers/billing_router.py
from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID

from ..adapters.dtos import BillingDTO, BillingCreateDTO
from ..services import BillingService

billing_router = APIRouter(
    prefix="/billings",
    tags=["Billings"],
)

# Instanciar o serviço
billing_service = BillingService()

@billing_router.get("/", response_model=List[BillingDTO])
def list_billings():
    return billing_service.list_billings()

@billing_router.post("/", response_model=BillingDTO)
def create_billing(billing_data: BillingCreateDTO):
    return billing_service.create_billing(billing_data)

@billing_router.get("/{billing_id}", response_model=BillingDTO)
def get_billing(billing_id: UUID):
    return billing_service.get_billing(billing_id)

@billing_router.put("/{billing_id}", response_model=BillingDTO)
def update_billing(billing_id: UUID, billing_data: BillingCreateDTO):
    return billing_service.update_billing(billing_id, billing_data)

@billing_router.delete("/{billing_id}", response_model=BillingDTO)
def delete_billing(billing_id: UUID):
    return billing_service.delete_billing(billing_id)
