import logging
import requests
import json
import time

from .comment_poster import CommentPoster
from ...adapters.dtos import UserPreferDTO

logger = logging.getLogger(__name__)

class GitHubCommentPoster(CommentPoster):
    """
    Implementação do poster de comentários para GitHub.
    """

    def post_comment(self, user_prefer: UserPreferDTO, comment: str):
        """
        Posta um comentário em um pull request do GitHub.
        
        Args:
            user_prefer: Preferências e dados do usuário
            comment: Comentário a ser postado
            
        Returns:
            dict: Resposta da API do GitHub
        """
        # Validar dados necessários
        logger.info(f"[GITHUB-POSTER] Preparando para postar comentário no GitHub")
        
        if not user_prefer.repository.owner or not user_prefer.repository.repo:
            logger.error(f"[GITHUB-POSTER] Owner e repo são obrigatórios: Owner={user_prefer.repository.owner}, Repo={user_prefer.repository.repo}")
            raise ValueError("Owner e repo são obrigatórios para postar em GitHub")
            
        pr_number = user_prefer.repository.pull_request_number
        
        # Se não tiver número de PR, criar uma nova issue
        if not pr_number:
            logger.warning(f"[GITHUB-POSTER] Nenhum número de Pull Request fornecido - criando nova issue")
            
            # Construir URL para criar uma nova issue
            create_issue_url = f'https://api.github.com/repos/{user_prefer.repository.owner}/{user_prefer.repository.repo}/issues'
            logger.info(f"[GITHUB-POSTER] URL para criar issue: {create_issue_url}")
            
            # Configurar cabeçalhos
            headers = {
                'Authorization': f'token {user_prefer.token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            # Preparar dados para a issue
            issue_data = {
                'title': 'Análise de Código Automatizada',
                'body': comment
            }
            
            logger.info(f"[GITHUB-POSTER] Criando nova issue com análise de código")
            
            try:
                # Criar a issue
                create_response = requests.post(create_issue_url, headers=headers, json=issue_data)
                
                if create_response.status_code in [201, 200]:
                    result = create_response.json()
                    logger.info(f"[GITHUB-POSTER] Issue criada com sucesso - Número: {result.get('number')}")
                    logger.info(f"[GITHUB-POSTER] URL da issue: {result.get('html_url')}")
                    return result
                else:
                    logger.error(f"[GITHUB-POSTER] Erro ao criar issue - Status: {create_response.status_code}")
                    logger.error(f"[GITHUB-POSTER] Resposta: {create_response.text}")
                    raise Exception(f'Erro ao criar issue: {create_response.status_code} - {create_response.text}')
            
            except requests.exceptions.RequestException as e:
                logger.error(f"[GITHUB-POSTER] Erro de requisição ao criar issue: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"[GITHUB-POSTER] Erro inesperado ao criar issue: {str(e)}")
                raise
        else:
            logger.info(f"[GITHUB-POSTER] Usando PR #{pr_number} como destino do comentário")
            
            # Construir URL para API do GitHub para comentar em um PR existente
            url = f'https://api.github.com/repos/{user_prefer.repository.owner}/{user_prefer.repository.repo}/issues/{pr_number}/comments'
            logger.info(f"[GITHUB-POSTER] URL da API: {url}")
            
            # Configurar cabeçalhos
            headers = {
                'Authorization': f'token {user_prefer.token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            logger.info(f"[GITHUB-POSTER] Cabeçalhos configurados - Token: {user_prefer.token[:5]}...")
            
            # Preparar dados
            data = {
                'body': comment
            }
            logger.info(f"[GITHUB-POSTER] Corpo do comentário preparado - Tamanho: {len(comment)} caracteres")
            
            # Fazer requisição para a API
            logger.info(f"[GITHUB-POSTER] Enviando comentário para GitHub...")
            start_time = time.time()
            
            try:
                response = requests.post(url, headers=headers, json=data)
                request_time = time.time() - start_time
                logger.info(f"[GITHUB-POSTER] Resposta recebida em {request_time:.2f} segundos - Status: {response.status_code}")
                
                # Verificar resposta
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"[GITHUB-POSTER] Comentário postado com sucesso - ID: {result.get('id')}")
                    logger.info(f"[GITHUB-POSTER] URL do comentário: {result.get('html_url')}")
                    return result
                else:
                    logger.error(f"[GITHUB-POSTER] Erro ao postar comentário - Status: {response.status_code}")
                    logger.error(f"[GITHUB-POSTER] Resposta: {response.text}")
                    raise Exception(f'Erro: {response.status_code} - {response.text}')
            
            except requests.exceptions.RequestException as e:
                logger.error(f"[GITHUB-POSTER] Erro de requisição: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"[GITHUB-POSTER] Erro inesperado: {str(e)}")
                raise
