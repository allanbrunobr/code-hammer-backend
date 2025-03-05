from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..services.integration import IntegrationService
from uuid import UUID

integrations_router = APIRouter(
    prefix="/api/v1/integrations",
    tags=["Integrations"],
)

integration_service = IntegrationService()

@integrations_router.get("/pull-requests")
async def get_pull_requests(repository_url: str, integration_id: str, db: Session = Depends(get_db)):
    """
    Busca os pull requests abertos para um repositório específico.
    """
    try:
        # Convert integration_id to UUID
        try:
            integration_id_uuid = UUID(integration_id)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Invalid integration_id format: {integration_id}")
            
        pull_requests = integration_service.get_open_pr(db, repository_url, integration_id_uuid)
        if not pull_requests:
            return []
        # Ensure we always return a list of PRs
        if isinstance(pull_requests, list):
            return pull_requests
        return [pull_requests]  # Wrap single PR in list for backwards compatibility
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
