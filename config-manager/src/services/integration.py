import logging
import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
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
        try:
            logging.info(f"Entering create_integration with data: {integration_data}")
            new_integration = self.repository.create_integration(db, integration_data)
            logging.info(f"Exiting create_integration with integration: {new_integration}")
            return new_integration
        except Exception as e:
            logging.error(f"Error creating integration: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating integration: {str(e)}"
            )

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

    def list_integrations(self, db: Session, user_id: Optional[UUID] = None) -> List[IntegrationDTO]:
        try:
            return self.repository.list_integrations(db, user_id)
        except Exception as e:
            logging.error(f"Error listing integrations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing integrations: {str(e)}")

    def get_open_pr(self, db: Session, repository_url: str) -> Optional[dict]:
        """Checks if there's an open PR for the given repository URL.
        
        Args:
            db: Database session
            repository_url: Repository URL to check for open PRs
            
        Returns:
            Optional[dict]: Information about the open PR or None if not found
        """
        try:
            logging.info(f"Checking for open PRs for repository: {repository_url}")
            
            # Extract owner and repo from URL
            parts = repository_url.replace("https://", "").replace("http://", "").split("/")
            if len(parts) < 2:
                logging.error(f"Invalid repository URL format: {repository_url}")
                return None
                
            owner = parts[-2]
            repo = parts[-1]
            logging.info(f"Extracted owner/repo: {owner}/{repo}")
            
            # Find integration with matching repository URL
            integrations = self.repository.list_integrations(db)
            matching_integration = None
            
            for integration in integrations:
                if integration.repository_url and integration.repository_url.lower() == repository_url.lower():
                    matching_integration = integration
                    break
                    
            if not matching_integration:
                logging.warning(f"No integration found for repository URL: {repository_url}")
                return None
                
            # For now, we'll return a mock PR
            # In a real implementation, you would use the GitHub API to check for open PRs
            mock_pr = {
                "number": 1,
                "title": "Mock PR for testing",
                "html_url": f"https://github.com/{owner}/{repo}/pull/1"
            }
            
            logging.info(f"Returning mock PR: {mock_pr}")
            return mock_pr
            
        except Exception as e:
            logging.error(f"Error checking for open PRs: {str(e)}")
            return None
