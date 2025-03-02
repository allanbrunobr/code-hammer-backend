from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..services.integration import IntegrationService

integrations_router = APIRouter(
    prefix="/api/v1/integrations",
    tags=["Integrations"],
)

integration_service = IntegrationService()

@integrations_router.get("/pull-requests")
async def get_pull_requests(repository_url: str, db: Session = Depends(get_db)):
    """
    Busca os pull requests abertos para um repositório específico.
    """
    try:
        pull_requests = integration_service.get_open_pr(db, repository_url)
        if not pull_requests:
            return []
        return [pull_requests]  # Retorna como lista para manter compatibilidade com o frontend
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
