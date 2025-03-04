"""
Middleware para autenticação e autorização.
Este módulo contém funções para validar o acesso de usuários às APIs.
"""
import logging
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID

from ...repositories.user import UserRepository

# Configurando o logger
logger = logging.getLogger(__name__)

# Define o esquema de autenticação
security = HTTPBearer()

async def validate_user_access(
    request: Request,
    user_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Valida se o usuário tem acesso ao recurso solicitado.
    
    Args:
        request: Objeto da requisição.
        user_id: ID do usuário a ser acessado.
        credentials: Credenciais de autenticação.
        
    Raises:
        HTTPException: Se o acesso for inválido.
    """
    try:
        # Obter o token
        token = credentials.credentials
        
        # Verificar o token (simplificado por enquanto)
        # Em um sistema real, você deve verificar o token JWT ou outro mecanismo
        # adequado para autenticação (ex.: via OAuth ou usando um serviço de identidade)
        
        # Aqui, vamos apenas verificar se o usuário existe
        user_repository = UserRepository()
        user = user_repository.get_user_by_id(None, user_id)
        
        if not user:
            logger.error(f"Usuário não encontrado: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Em um sistema real, você também verificaria se o token pertence ao usuário
        # ou se o usuário tem permissão para acessar os recursos de outro usuário
        
        # Adicionar o usuário ao request para uso posterior
        request.state.user = user
        
        logger.info(f"Acesso validado para o usuário: {user_id}")
        
    except HTTPException:
        # Repassar exceções HTTP
        raise
    except Exception as e:
        logger.error(f"Erro na validação de acesso: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso não autorizado"
        )
