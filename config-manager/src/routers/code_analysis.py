import logging
import requests
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ..core.db.database import get_db
from ..services.integration import IntegrationService
from ..services.user import UserService
from ..adapters.dtos import UserDTO
from ..services.auth import get_current_user
from ..utils.environment import Environment

code_analysis_router = APIRouter(
    prefix="/code-analysis",
    tags=["Code Analysis"],
)

integration_service = IntegrationService()
user_service = UserService()
logger = logging.getLogger(__name__)

@code_analysis_router.post("/analyze")
async def analyze_code(
    background_tasks: BackgroundTasks,
    code: str,
    integration_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: UserDTO = Depends(get_current_user)
):
    """
    Endpoint para análise de código utilizando a integração do usuário.
    
    Args:
        code: Código a ser analisado
        integration_id: ID opcional da integração a ser utilizada
                       (se não fornecido, utiliza a primeira disponível)
        current_user: Usuário autenticado
        
    Returns:
        JSONResponse: Confirmação de envio para análise
    """
    try:
        # Obtém as integrações do usuário
        integrations = integration_service.list_integrations(db, current_user.id)
        
        if not integrations:
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "Nenhuma integração configurada. Por favor, configure primeiro."
                },
                status_code=400
            )
            
        # Se não foi especificado um ID de integração, usa a primeira disponível
        integration = None
        if integration_id:
            # Filtra para encontrar a integração específica
            for integ in integrations:
                if str(integ.id) == str(integration_id):
                    integration = integ
                    break
                    
            if not integration:
                return JSONResponse(
                    content={
                        "status": "error",
                        "message": f"Integração com ID {integration_id} não encontrada"
                    },
                    status_code=404
                )
        else:
            # Usa a primeira integração
            integration = integrations[0]
        
        # Envia a análise em background para não bloquear a resposta
        background_tasks.add_task(
            _send_code_analysis_request,
            code=code,
            user_email=current_user.email,
            integration=integration
        )
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Código enviado para análise com sucesso",
                "integration": {
                    "id": str(integration.id),
                    "name": integration.name,
                    "repository": integration.repository
                }
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar análise de código: {str(e)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Erro ao processar análise: {str(e)}"
            },
            status_code=500
        )

async def _send_code_analysis_request(code: str, user_email: str, integration):
    """
    Função de background para enviar solicitação de análise de código
    
    Args:
        code: Código a ser analisado
        user_email: Email do usuário
        integration: Objeto de integração com dados do repositório
    """
    try:
        code_processor_url = Environment.get("CODE_PROCESSOR_URL", "http://code-processor:8084")
        url = f"{code_processor_url}/process"
        
        payload = {
            "code": code,
            "email": user_email,
        }
        
        logger.info(f"Enviando solicitação de análise para {url}")
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            logger.error(f"Erro na análise de código: {response.status_code} - {response.text}")
        else:
            logger.info(f"Código enviado com sucesso para análise")
            
    except Exception as e:
        logger.error(f"Erro ao enviar código para análise: {str(e)}")
