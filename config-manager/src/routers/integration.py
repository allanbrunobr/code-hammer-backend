import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from urllib.parse import unquote

from ..adapters.dtos import IntegrationDTO, IntegrationCreateDTO, UserDTO
from ..services import IntegrationService
from ..core.db.database import get_db
from ..services.auth import get_current_user

integration_router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)

integration_service = IntegrationService()

# Router separado para evitar conflitos com rotas dinâmicas
pull_request_router = APIRouter(
    prefix="/pull-requests",
    tags=["Pull Requests"],
)

@pull_request_router.get("/", response_model=Optional[List[dict]])
def get_open_pr(
    repository_url: str = Query(..., description="URL do repositório para verificar PRs abertos"),
    integration_id: str = Query(..., description="ID da integração a ser utilizada"),
    db: Session = Depends(get_db)
):
    """
    Checks if there's an open PR for the given repository URL using the specified integration.
    """
    logging.info("==================== DEBUG GET OPEN PR ENDPOINT ====================")
    logging.info(f"Repository URL recebida: {repository_url}")
    logging.info(f"Integration ID recebido: {integration_id}")
    logging.info(f"Tipo do Integration ID: {type(integration_id)}")
    
    try:
        try:
            integration_id_uuid = UUID(integration_id)
            logging.info(f"UUID convertido com sucesso: {integration_id_uuid}")
            result = integration_service.get_open_pr(db, repository_url, integration_id_uuid)
            if not result:
                return []
            return result if isinstance(result, list) else [result]
        except ValueError as e:
            logging.error(f"Erro ao converter integration_id para UUID: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Formato inválido para integration_id: {integration_id}. Erro: {str(e)}")
    except Exception as e:
        logging.error(f"Erro inesperado no endpoint get_open_pr: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar PRs abertos: {str(e)}")

@integration_router.get("/", response_model=List[IntegrationDTO])
def list_integrations(
    db: Session = Depends(get_db),
    user_id: Optional[UUID] = Query(None),
    current_user: UserDTO = Depends(get_current_user)
):
    logging.info("=== Integration List Debug ===")
    logging.info(f"Current user: {current_user.id}")
    logging.info(f"Requested user_id: {user_id}")
    
    try:
        # Authorization check
        if user_id and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this resource")

        user_id_to_use = user_id or current_user.id
        logging.info(f"Fetching integrations for user_id: {user_id_to_use}")
        
        result = integration_service.list_integrations(db, user_id_to_use)
        logging.info(f"Found {len(result)} integrations")
        return result
    except Exception as e:
        logging.error(f"Error in list_integrations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@integration_router.post("/", response_model=IntegrationDTO)
def create_integration_endpoint(integration: IntegrationCreateDTO, db: Session = Depends(get_db)):
    logging.info(f"Entering create_integration_endpoint with data: {integration}")
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
