import logging
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from ..adapters.dtos import IntegrationCreateDTO
from ..domain.integration import Integration


class IntegrationRepository:
    def get_integration_by_id(self, db: Session, integration_id: UUID) -> Optional[Integration]:
        return db.query(Integration).filter(Integration.id == integration_id).first()

    def list_integrations(self, db: Session, user_id: Optional[UUID] = None) -> List[Integration]:
        query = db.query(Integration)
        if user_id:
            query = query.filter(Integration.user_id == user_id)
        return query.all()

    def create_integration(self, db: Session, integration_data: IntegrationCreateDTO) -> Integration:
        try:
            data = integration_data.dict()
            logging.info(f"Entering create_integration with data: {data}")
            new_integration = Integration(**data)
            db.add(new_integration)
            db.commit()
            db.refresh(new_integration)
            logging.info(f"Exiting create_integration with integration: {new_integration}")
            return new_integration
        except Exception as e:
            db.rollback()
            logging.error(f"Error in create_integration: {str(e)}")
            raise

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
