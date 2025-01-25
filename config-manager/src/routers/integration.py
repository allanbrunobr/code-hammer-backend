from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..adapters.dtos import IntegrationDTO, IntegrationCreateDTO
from ..services import IntegrationService
from ..core.db.database import get_db

integration_router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)

integration_service = IntegrationService()

@integration_router.get("/", response_model=List[IntegrationDTO])
def list_integrations(db: Session = Depends(get_db)):
    return integration_service.list_integrations(db)

@integration_router.post("/", response_model=IntegrationDTO)
def create_integration_endpoint(integration: IntegrationCreateDTO, db: Session = Depends(get_db)):
    return integration_service.create_integration(db, integration)

@integration_router.get("/{integration_id}", response_model=IntegrationDTO)
def get_integration(integration_id: UUID, db: Session = Depends(get_db)):
    return integration_service.get_integration(db, integration_id)

@integration_router.put("/{integration_id}", response_model=IntegrationDTO)
def update_integration_endpoint(integration_id: UUID, integration: IntegrationCreateDTO, db: Session = Depends(get_db)):
    return integration_service.update_integration(db, integration_id, integration)

@integration_router.delete("/{integration_id}", response_model=IntegrationDTO)
def delete_integration_endpoint(integration_id: UUID, db: Session = Depends(get_db)):
    return integration_service.delete_integration(db, integration_id)
