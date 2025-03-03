import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from ..adapters.dtos import CodeAnalysisRequestDTO, CodeAnalysisResponseDTO, ApiResponseDTO
from ..core.db.database import get_db
from ..services import ProcessService
from ..services import UserService

user_service = UserService()
process_service = ProcessService()

logger = logging.getLogger(__name__)

analysis_router = APIRouter(
    prefix="/analysis",
    tags=["Code Analysis"],
)

@analysis_router.post("/", response_model=ApiResponseDTO[CodeAnalysisResponseDTO])
async def analyze_code(
    request: CodeAnalysisRequestDTO,
    db: Session = Depends(get_db)
):
    """
    Endpoint para solicitar análise de código.
    
    Args:
        request: Dados da solicitação de análise
        db: Sessão do banco de dados
        
    Returns:
        ApiResponseDTO: Resposta com status da solicitação
    """
    request_id = str(uuid.uuid4())
    logger.info(f"[CODE-PROCESSOR] Nova solicitação de análise - ID: {request_id}")
    logger.info(f"[CODE-PROCESSOR] Dados da solicitação: {json.dumps(request.dict(), default=str)}")
    
    try:
        # Obter usuário pelo email
        logger.info(f"[CODE-PROCESSOR] Buscando usuário com email: {request.email}")
        user = user_service.get_user_by_email(db, request.email)
        if not user:
            logger.error(f"[CODE-PROCESSOR] Usuário não encontrado para email: {request.email}")
            return ApiResponseDTO(
                success=False,
                message="User not found",
                timestamp=datetime.now(),
                errors=["No user found with the provided email address"]
            )
        
        logger.info(f"[CODE-PROCESSOR] Usuário encontrado: ID={user.id}, Nome={user.name}")
        
        # Verificar se o usuário está ativo
        if not user_service.verify_user_is_active(db, user.email):
            logger.error(f"[CODE-PROCESSOR] Usuário não está ativo: {user.email}")
            return ApiResponseDTO(
                success=False,
                message="User not active",
                timestamp=datetime.now(),
                errors=["User account is not active"]
            )
        
        # Obter preferências do usuário, incluindo dados de integração
        try:
            logger.info(f"[CODE-PROCESSOR] Buscando integração: {request.integration_id}")
            user_prefer = user_service.get_user_prefer(user, request.code, request.integration_id)
            logger.info(f"[CODE-PROCESSOR] Integração encontrada: Repo={user_prefer.repository.type}, URL={user_prefer.repository.repo}")
            logger.info(f"[CODE-PROCESSOR] Token de acesso: {user_prefer.token[:5]}...")
            
            # Atualizar com valores da requisição
            user_prefer.language = request.language
            logger.info(f"[CODE-PROCESSOR] Idioma definido: {user_prefer.language}")
            
            if request.pull_request_number:
                user_prefer.repository.pull_request_number = request.pull_request_number
                
            # Personalizar o prompt de acordo com os tipos de análise solicitados
            prompt_parts = []
            
            if "all" in [t.value for t in request.analysis_types]:
                # Se 'all' estiver presente, usar prompt completo
                prompt_parts.append("analyze this code for quality, security, performance, bugs, code smells, and vulnerabilities")
                prompt_parts.append("comment if the code follows the fundamentals of OWASP and SOLID principles")
                logger.info(f"[CODE-PROCESSOR] Tipo de análise: completa")
            else:
                # Caso contrário, construir prompt baseado nos tipos de análise solicitados
                analysis_mappings = {
                    "codeQuality": "code quality",
                    "security": "security issues",
                    "performance": "performance optimizations",
                    "bugs": "bugs and logical errors",
                    "codeSmells": "code smells",
                    "vulnerabilities": "security vulnerabilities",
                    "owasp": "OWASP principles",
                    "solid": "SOLID principles"
                }
                
                selected_analyses = []
                for analysis_type in request.analysis_types:
                    if analysis_type.value in analysis_mappings:
                        selected_analyses.append(analysis_mappings[analysis_type.value])
                
                if selected_analyses:
                    prompt_parts.append(f"analyze this code for: {', '.join(selected_analyses)}")
                    logger.info(f"[CODE-PROCESSOR] Tipos de análise selecionados: {', '.join(selected_analyses)}")
            
            # Incluir informações do arquivo se fornecidas
            if request.file_name:
                prompt_parts.append(f"The code is from a file named '{request.file_name}'")
                logger.info(f"[CODE-PROCESSOR] Nome do arquivo: {request.file_name}")
            
            # Construir prompt personalizado
            custom_prompt = "You are an expert code analyst. " + " and ".join(prompt_parts) + "."
            custom_prompt += "\n\n{code}\n\nYou should format in markdown translated to {language}"
            
            # Atualizar o prompt no user_prefer
            user_prefer.prompt = custom_prompt
            logger.info(f"[CODE-PROCESSOR] Prompt personalizado criado com {len(custom_prompt)} caracteres")
            
            # Verificar se há código fornecido ou se deve analisar todo o projeto
            if not request.code and not user_prefer.repository.pull_request_number:
                logger.info(f"[CODE-PROCESSOR] Nenhum código fornecido e nenhum PR encontrado - analisando todo o projeto")
                # Definir flag para analisar todo o projeto
                user_prefer.analyze_full_project = True
            
            # Enviar mensagem para processamento
            logger.info(f"[CODE-PROCESSOR] Enviando mensagem para Pub/Sub")
            message_id = process_service.sent_message(user_prefer)
            
            logger.info(f"[CODE-PROCESSOR] Mensagem enviada com sucesso para Pub/Sub - ID: {message_id}")
            
            response_data = CodeAnalysisResponseDTO(
                request_id=request_id,
                message="Code analysis request received. Results will be processed in the background.",
                status="processing"
            )
            
            return ApiResponseDTO(
                success=True,
                message="Code analysis request submitted successfully",
                timestamp=datetime.now(),
                data=response_data
            )
            
        except ValueError as ve:
            logger.error(f"[CODE-PROCESSOR] Erro nas preferências do usuário: {str(ve)}")
            return ApiResponseDTO(
                success=False,
                message="Invalid request parameters",
                timestamp=datetime.now(),
                errors=[str(ve)]
            )
        
    except Exception as e:
        logger.exception(f"[CODE-PROCESSOR] Erro ao processar solicitação de análise: {str(e)}")
        return ApiResponseDTO(
            success=False,
            message="Internal server error",
            timestamp=datetime.now(),
            errors=[str(e)]
        )
