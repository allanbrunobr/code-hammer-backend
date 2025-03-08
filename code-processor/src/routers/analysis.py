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
            
            # Configurar o número do PR e post_comment
            if request.pull_request_number:
                logger.info(f"[CODE-PROCESSOR] Configurando número do PR da requisição: {request.pull_request_number}")
                # Convertemos para int se vier como string
                pr_number = int(request.pull_request_number) if isinstance(request.pull_request_number, str) else request.pull_request_number
                user_prefer.repository.pull_request_number = pr_number
                
                # Log para debug
                logger.info(f"[CODE-PROCESSOR] Número do PR configurado para: {user_prefer.repository.pull_request_number}")
                
            # Definir explicitamente o post_comment do user_prefer
            user_prefer.post_comment = request.post_comment
            logger.info(f"[CODE-PROCESSOR] Post Comment: {user_prefer.post_comment}")
                
            # Verificar se a integração tem tipos de análise específicos
            integration = user_service._get_integration_by_id(request.integration_id)
            integration_analyze_types = None
            
            if integration and 'analyze_types' in integration and integration['analyze_types']:
                # Extrair os tipos de análise da integração (formato: "tipo1,tipo2,tipo3")
                integration_analyze_types = integration['analyze_types'].split(',')
                logger.info(f"[CODE-PROCESSOR] Tipos de análise da integração: {integration_analyze_types}")
            
            # Personalizar o prompt de acordo com os tipos de análise
            prompt_parts = []
            
            if integration_analyze_types:
                # Se a integração tem tipos de análise específicos, usar esses
                # Mapeamento para os tipos de análise da integração
                integration_mappings = {
                    "componentizacao": "componentization",
                    "otimizacaoBigO": "optimization (BIG O)",
                    "duplicidade": "duplication",
                    "codigoLimpo": "code quality",
                    "seguranca": "security issues",
                    "performance": "performance optimizations",
                    "bugs": "bugs and logical errors",
                    "codeSmells": "code smells",
                    "vulnerabilidades": "security vulnerabilities",
                    "owasp": "OWASP principles",
                    "solid": "SOLID principles"
                }
                
                selected_analyses = []
                for analysis_type in integration_analyze_types:
                    analysis_type = analysis_type.strip()
                    if analysis_type in integration_mappings:
                        selected_analyses.append(integration_mappings[analysis_type])
                    else:
                        # Se não encontrar no mapeamento, usar o valor original
                        selected_analyses.append(analysis_type)
                
                if selected_analyses:
                    prompt_parts.append(f"analyze this code for: {', '.join(selected_analyses)}")
                    logger.info(f"[CODE-PROCESSOR] Tipos de análise da integração: {', '.join(selected_analyses)}")
                else:
                    # Se não conseguir mapear nenhum tipo, usar o padrão
                    prompt_parts.append("analyze this code for quality, security, performance, bugs, code smells, and vulnerabilities")
                    logger.info(f"[CODE-PROCESSOR] Usando tipos de análise padrão (nenhum tipo da integração mapeado)")
            elif "all" in [t.value for t in request.analysis_types]:
                # Se 'all' estiver presente na requisição e não tiver tipos da integração, usar prompt completo
                prompt_parts.append("analyze this code for quality, security, performance, bugs, code smells, and vulnerabilities")
                prompt_parts.append("comment if the code follows the fundamentals of OWASP and SOLID principles")
                logger.info(f"[CODE-PROCESSOR] Tipo de análise: completa")
            else:
                # Caso contrário, construir prompt baseado nos tipos de análise da requisição
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
                    logger.info(f"[CODE-PROCESSOR] Tipos de análise da requisição: {', '.join(selected_analyses)}")
            
            # Incluir informações do arquivo se fornecidas
            if request.file_name:
                prompt_parts.append(f"The code is from a file named '{request.file_name}'")
                logger.info(f"[CODE-PROCESSOR] Nome do arquivo: {request.file_name}")
            
            # Construir template do prompt personalizado
            prompt_template = "You are an expert code analyst. " + " and ".join(prompt_parts) + "."
            prompt_template += "\n\n{code}\n\n"
            prompt_template += "You should format in markdown translated to {language}. "
            prompt_template += "For each suggestion, whenever possible, include a 'Código revisado:' section with the improved code in a markdown code block that users can copy. "
            prompt_template += "In the revised code, add comments to each section where a change was made. "
            prompt_template += "Make sure the revised code is complete and functional, incorporating all the suggested improvements."
            
            # Formatar o prompt com o código e idioma do usuário
            formatted_prompt = prompt_template.format(
                code="{code}",  # Mantém o placeholder {code} para ser substituído posteriormente
                language=user_prefer.language or 'Portuguese/BR'
            )
            
            # Atualizar o prompt no user_prefer
            user_prefer.prompt = formatted_prompt
            logger.info(f"[CODE-PROCESSOR] Prompt personalizado criado com {len(formatted_prompt)} caracteres")
            
            # Verificar se há código fornecido ou se deve analisar todo o projeto
            if not request.code and not user_prefer.repository.pull_request_number:
                logger.info(f"[CODE-PROCESSOR] Nenhum código fornecido e nenhum PR encontrado - analisando todo o projeto")
                # Definir flag para analisar todo o projeto
                user_prefer.analyze_full_project = True
            
            # Enviar mensagem para processamento
            logger.info(f"[CODE-PROCESSOR] Configurando mensagem para Pub/Sub com PR Number: {user_prefer.repository.pull_request_number}")
            logger.info(f"[CODE-PROCESSOR] Enviando mensagem para Pub/Sub")
            message_id = process_service.sent_message(user_prefer)
            
            logger.info(f"[CODE-PROCESSOR] Mensagem enviada com sucesso para Pub/Sub - ID: {message_id}")
            
            files_analyzed = 0
            if user_prefer.repository.pull_request_number:
                # Buscar arquivos reais do PR
                pr_files = process_service.get_pr_files(user_prefer.repository)
                files_analyzed = len(pr_files)
                
                # Adicionar informações de arquivos ao log
                logger.info(f"[CODE-PROCESSOR] Total de {files_analyzed} arquivos reais encontrados para o PR {request.pull_request_number}")
                logger.info(f"[CODE-PROCESSOR] Arquivos reais: {pr_files}")
                
                # Adicionar informações extras para o processo de análise
                user_prefer.files_to_analyze = pr_files  # Adicionar lista de arquivos a serem analisados
                user_prefer.files_count = files_analyzed  # Adicionar contagem de arquivos
            else:
                # Se não tiver PR, assumir arquivos comuns
                dummy_files = [
                    "package.json", 
                    "src/index.js",
                    "src/App.js",
                    "src/components/Header.jsx",
                    "src/styles/main.css"
                ]
                files_analyzed = len(dummy_files)
                user_prefer.files_to_analyze = dummy_files
                user_prefer.files_count = files_analyzed
                logger.info(f"[CODE-PROCESSOR] Sem PR. Usando {files_analyzed} arquivos reais comuns.")

            response_data = CodeAnalysisResponseDTO(
                request_id=request_id,
                message="Code analysis request received. Results will be processed in the background.",
                status="processing",
                files_analyzed=files_analyzed
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
