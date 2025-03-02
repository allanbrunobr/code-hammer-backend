from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import logging
from typing import Any, Optional, Dict

from ..adapters.dtos import ProcessRequestDTO, ApiResponseDTO
from ..core.db.database import get_db
from ..services import ProcessService
from ..services import UserService

user_service = UserService()
process_service = ProcessService()

logger = logging.getLogger(__name__)

process_router = APIRouter(
    prefix="/process",
    tags=["Process"],
)

@process_router.post("/")
def process(
    process_request: ProcessRequestDTO,
    db: Session = Depends(get_db)
) -> ApiResponseDTO:
    """
    Endpoint to process a code analysis request.

    Args:
        process_request (ProcessRequestDTO): Processing request data.
        db (Session): Database session.

    Returns:
        ApiResponseDTO: Response with success or error status.
    """
    try:
        # Gerar ID único para a solicitação
        request_id = str(uuid.uuid4())
        
        # Obter usuário pelo email
        user = user_service.get_user_by_email(db, process_request.email)
        if not user:
            logger.error(f"Usuário não encontrado para email: {process_request.email}")
            return ApiResponseDTO(
                success=False,
                message="User not found",
                timestamp=datetime.now(),
                errors=["User not found with the provided email"]
            )
        
        # Verificar se o usuário está ativo
        if not user_service.verify_user_is_active(db, user.email):
            logger.error(f"Usuário não está ativo: {user.email}")
            return ApiResponseDTO(
                success=False,
                message="User not active",
                timestamp=datetime.now(),
                errors=["User account is not active"]
            )

        # Obter preferências do usuário, incluindo dados de integração
        try:
            user_prefer = user_service.get_user_prefer(user, process_request.code)
            
            # Se um token foi fornecido na requisição, usar ele
            if process_request.token:
                user_prefer.token = process_request.token
                
            # Se uma URL de PR foi fornecida, extrair informações para o repositório
            if process_request.url_pr:
                # Implementação simplificada - em um caso real, você extrairia mais informações
                logger.info(f"PR URL fornecida: {process_request.url_pr}")
            
            # Enviar para processamento
            process_service.sent_message(user_prefer)
            
            return ApiResponseDTO(
                success=True,
                message="Code analysis request submitted successfully",
                timestamp=datetime.now(),
                data={"request_id": request_id}
            )
            
        except ValueError as ve:
            logger.error(f"Erro nas preferências do usuário: {str(ve)}")
            return ApiResponseDTO(
                success=False,
                message="Invalid request parameters",
                timestamp=datetime.now(),
                errors=[str(ve)]
            )

    except Exception as e:
        logger.exception(f"Ocorreu um erro: {e}")
        return ApiResponseDTO(
            success=False,
            message="Internal server error",
            timestamp=datetime.now(),
            errors=[str(e)]
        )
