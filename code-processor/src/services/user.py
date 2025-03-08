import logging
import requests
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID

from ..adapters.dtos import UserPreferDTO, RepositoryDTO, TypeRepositoryEnum
from ..domain import User
from ..utils.environment import Environment

logger = logging.getLogger(__name__)

# Corrigindo a URL do config-manager para usar a porta 8082 em vez de 8083
#CONFIG_MANAGER_URL = Environment.get("CONFIG_MANAGER_URL", "http://localhost:8082")
CONFIG_MANAGER_URL = "http://localhost:8082"

class UserService:

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        logger.info(f"[USER-SERVICE] Buscando usuário com email: {email}")
        user = db.query(User).filter(User.email == email).first()
        if user:
            logger.info(f"[USER-SERVICE] Usuário encontrado: ID={user.id}, Nome={user.name}")
        else:
            logger.warning(f"[USER-SERVICE] Usuário não encontrado para email: {email}")
        return user

    @staticmethod
    def verify_user_is_active(db: Session, email: str) -> bool:
        # Implementação simplificada - na prática você poderia verificar o status do usuário
        logger.info(f"[USER-SERVICE] Verificando se usuário está ativo: {email}")
        return True

    @staticmethod
    def get_user_prefer(user: User, code: str, integration_id: str = None) -> UserPreferDTO:
        """Obtém as preferências do usuário, utilizando a integração especificada
        
        Args:
            user: Usuário para o qual buscar preferências
            code: Código a ser analisado
            integration_id: ID da integração a ser usada
            
        Returns:
            UserPreferDTO: Objeto com as preferências e dados de integração
        """
        try:
            logger.info(f"[USER-SERVICE] Obtendo preferências para usuário: {user.email}")
            logger.info(f"[USER-SERVICE] Código fornecido: {'Vazio' if not code else f'{len(code)} caracteres'}")
            logger.info(f"[USER-SERVICE] ID da integração solicitada: {integration_id}")
            
            if not integration_id:
                logger.error(f"[USER-SERVICE] ID da integração não fornecido")
                raise ValueError("ID da integração não fornecido")
                
            # Buscar integração específica diretamente pelo ID
            integration = UserService._get_integration_by_id(integration_id)
            
            if not integration:
                logger.error(f"[USER-SERVICE] Integração com ID {integration_id} não encontrada")
                raise ValueError(f"Integração com ID {integration_id} não encontrada")
            
            logger.info(f"[USER-SERVICE] Usando integração: {integration['name']} para o repositório: {integration['repository']}")
            logger.info(f"[USER-SERVICE] URL do repositório: {integration['repository_url']}")
            logger.info(f"[USER-SERVICE] Token encontrado: {integration['repository_token'][:5]}...") if integration['repository_token'] else logger.info("[USER-SERVICE] Token não encontrado na integração")
            
            # Definir o prompt de análise
            prompt = '''
                You are an expert code analyst, you should analyze this code and comment and refactor the parts of code with bugs, vulnerabilities and code smells.
                You should comment if the code follows the fundamentals of OWASP and SOLID.
                
                {code}
                
                You should format in markdown translated to {language}
            '''
            
            # Formatar o prompt com o código e idioma
            formatted_prompt = prompt.format(code=code, language=user.language or 'Portuguese/BR')
            logger.info(f"[USER-SERVICE] Prompt formatado com {len(formatted_prompt)} caracteres")
            
            # Mapear o tipo de repositório
            repo_type = UserService._map_repository_type(integration['repository'])
            logger.info(f"[USER-SERVICE] Tipo de repositório mapeado: {repo_type}")
            
            # Extrair informações do URL do repositório
            owner, repo = UserService._extract_repo_info(integration['repository_url'])
            logger.info(f"[USER-SERVICE] Owner/Repo extraídos: {owner}/{repo}")
            
            # Obter número do pull request se aplicável
            pull_request_number = integration.get('pull_request_number')
            logger.info(f"[USER-SERVICE] Número do Pull Request da integração: {pull_request_number or 'Não fornecido'}")

            # Se o PR já está na integração, não precisamos buscar por PRs abertos
            # Esta busca só é necessária quando não temos o número do PR
            if not pull_request_number and not code:
                logger.info(f"[USER-SERVICE] Sem PR e sem código fornecido, tentando buscar PR aberto")
                try:
                    logger.info(f"[USER-SERVICE] Tentando obter PR aberto para o repositório: {integration['repository_url']}")
                    pr_info = UserService._get_open_pr(integration['repository_url'])
                    if pr_info and 'number' in pr_info:
                        pull_request_number = str(pr_info['number'])
                        logger.info(f"[USER-SERVICE] PR aberto encontrado: #{pull_request_number}")
                    else:
                        logger.info("[USER-SERVICE] Nenhum PR aberto encontrado para o repositório")
                except Exception as e:
                    logger.warning(f"[USER-SERVICE] Erro ao buscar PR aberto: {str(e)}")
                    # Mesmo com erro, continuamos o fluxo
            else:
                logger.info(f"[USER-SERVICE] Já temos o número do PR ou código para analisar, não precisamos buscar PR aberto")
            
            # Criar o objeto RepositoryDTO
            repository = RepositoryDTO(
                type=repo_type,
                token=integration['repository_token'],
                owner=owner,
                repo=repo,
                pull_request_number=pull_request_number,
                integration_id=integration_id
            )
            
            # Criação do objeto UserPreferDTO
            user_prefer = UserPreferDTO(
                language=user.language or 'Portuguese/BR',
                prompt=formatted_prompt,
                name=user.name,
                code=code,
                email=user.email,
                token=integration['repository_token'],
                repository=repository,
                post_comment=True  # Por padrão, habilitar post de comentários no PR
            )
            
            logger.info(f"[USER-SERVICE] UserPreferDTO criado com sucesso")
            return user_prefer
            
        except Exception as e:
            logger.error(f"[USER-SERVICE] Erro ao obter preferências do usuário: {str(e)}")
            raise
    
    @staticmethod
    def _get_integration_by_id(integration_id: str) -> dict:
        """Busca uma integração específica pelo ID no config-manager
        
        Args:
            integration_id: ID da integração
            
        Returns:
            dict: Dados da integração ou None se não encontrada
        """
        try:
            url = f"{CONFIG_MANAGER_URL}/api/v1/integrations/{integration_id}"
            logger.info(f"[USER-SERVICE] Buscando integração com ID {integration_id} em: {url}")
            
            headers = {"Authorization": f"Bearer {Environment.get('API_TOKEN', '')}", "Accept": "application/json"}
            response = requests.get(url, headers=headers)
            logger.info(f"[USER-SERVICE] Status da resposta: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    integration = response.json()
                    logger.info(f"[USER-SERVICE] Integração encontrada: {integration.get('name')}")
                    return integration
                except Exception as e:
                    logger.error(f"[USER-SERVICE] Erro ao processar resposta JSON: {str(e)}")
                    return None
            else:
                logger.error(f"[USER-SERVICE] Erro ao buscar integração: Status {response.status_code}")
                logger.error(f"[USER-SERVICE] Resposta: {response.text}")
                return None
        except Exception as e:
            logger.error(f"[USER-SERVICE] Erro ao buscar integração: {str(e)}")
            return None
    
    @staticmethod
    def _map_repository_type(repo_type: str) -> TypeRepositoryEnum:
        """Mapeia o tipo de repositório para o enum
        
        Args:
            repo_type: Tipo de repositório como string
            
        Returns:
            TypeRepositoryEnum: Tipo de repositório como enum
        """
        type_map = {
            'github': TypeRepositoryEnum.GITHUB,
            'gitlab': TypeRepositoryEnum.GITLAB,
            'azure': TypeRepositoryEnum.AZURE,
            'bitbucket': TypeRepositoryEnum.BITBUCKET
        }
        
        # Default para GitHub se não for reconhecido
        result = type_map.get(repo_type.lower(), TypeRepositoryEnum.GITHUB)
        logger.info(f"[USER-SERVICE] Tipo de repositório mapeado: {repo_type} -> {result}")
        return result
    
    @staticmethod
    def _extract_repo_info(repo_url: str) -> tuple:
        """Extrai o owner e nome do repositório a partir da URL
        
        Args:
            repo_url: URL do repositório
            
        Returns:
            tuple: (owner, repo)
        """
        if not repo_url:
            logger.warning("[USER-SERVICE] URL do repositório vazia")
            return "unknown", "unknown"
            
        # Remover protocolo se existir
        if '://' in repo_url:
            repo_url = repo_url.split('://')[-1]
        
        # Remover domínio e extrair partes
        parts = repo_url.split('/')
        
        # Assumir formato padrão username/repo
        if len(parts) >= 2:
            owner = parts[-2]
            repo = parts[-1]
            logger.info(f"[USER-SERVICE] Extraído da URL {repo_url}: owner={owner}, repo={repo}")
            return owner, repo
        
        logger.warning(f"[USER-SERVICE] Formato de URL de repositório não reconhecido: {repo_url}")
        return "unknown", "unknown"
        
    @staticmethod
    def _get_open_pr(repository_url: str) -> Optional[dict]:
        """Busca um PR aberto para o repositório
        
        Args:
            repository_url: URL do repositório
            
        Returns:
            Optional[dict]: Informações do PR aberto ou None se não encontrado
        """
        try:
            url = f"{CONFIG_MANAGER_URL}/api/v1/integrations/open_pr"
            logger.info(f"[USER-SERVICE] Buscando PR aberto para repositório: {repository_url}")
            
            headers = {"Authorization": f"Bearer {Environment.get('API_TOKEN', '')}", "Accept": "application/json"}
            params = {"repository_url": repository_url}
            
            response = requests.get(url, headers=headers, params=params)
            logger.info(f"[USER-SERVICE] Status da resposta: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    pr_info = response.json()
                    if pr_info:
                        logger.info(f"[USER-SERVICE] PR aberto encontrado: {pr_info}")
                        return pr_info
                    else:
                        logger.info("[USER-SERVICE] Nenhum PR aberto encontrado")
                        return None
                except Exception as e:
                    logger.error(f"[USER-SERVICE] Erro ao processar resposta JSON: {str(e)}")
                    return None
            else:
                logger.error(f"[USER-SERVICE] Erro ao buscar PR aberto: Status {response.status_code}")
                logger.error(f"[USER-SERVICE] Resposta: {response.text}")
                return None
        except Exception as e:
            logger.error(f"[USER-SERVICE] Erro ao buscar PR aberto: {str(e)}")
            return None
