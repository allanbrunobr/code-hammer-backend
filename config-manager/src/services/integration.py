from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from uuid import UUID

from ..adapters.dtos import IntegrationDTO, IntegrationCreateDTO
from ..repositories import IntegrationRepository

class IntegrationService:
    def __init__(self):
        self.repository = IntegrationRepository()

    def get_integration(self, db: Session, integration_id: UUID) -> IntegrationDTO:
        integration = self.repository.get_integration_by_id(db, integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        return integration

    def create_integration(self, db: Session, integration_data: IntegrationCreateDTO) -> IntegrationDTO:
        new_integration = self.repository.create_integration(db, integration_data)
        return new_integration

    def update_integration(self, db: Session, integration_id: UUID, integration_data: IntegrationCreateDTO) -> IntegrationDTO:
        updated_integration = self.repository.update_integration(db, integration_id, integration_data)
        if not updated_integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        return updated_integration

    def delete_integration(self, db: Session, integration_id: UUID) -> IntegrationDTO:
        deleted_integration = self.repository.delete_integration(db, integration_id)
        if not deleted_integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        return deleted_integration

    def list_integrations(self, db: Session) -> List[IntegrationDTO]:
        return self.repository.list_integrations(db)
