from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from ..adapters.dtos import IntegrationCreateDTO
from ..domain import Integration


class IntegrationRepository:
    def get_integration_by_id(self, db: Session, integration_id: UUID) -> Optional[Integration]:
        return db.query(Integration).filter(Integration.uuid == integration_id).first()

    def list_integrations(self, db: Session) -> List[Integration]:
        return db.query(Integration).all()

    def create_integration(self, db: Session, integration_data: IntegrationCreateDTO) -> Integration:
        new_integration = Integration(**integration_data.dict())
        db.add(new_integration)
        db.commit()
        db.refresh(new_integration)
        return new_integration

    def update_integration(self, db: Session, integration_id: UUID, integration_data: IntegrationCreateDTO) -> Optional[Integration]:
        integration = self.get_integration_by_id(db, integration_id)
        if integration:
            for key, value in integration_data.dict().items():
                setattr(integration, key, value)
            db.commit()
            db.refresh(integration)
        return integration

    def delete_integration(self, db: Session, integration_id: UUID) -> Optional[Integration]:
        integration = self.get_integration_by_id(db, integration_id)
        if integration:
            db.delete(integration)
            db.commit()
        return integration
