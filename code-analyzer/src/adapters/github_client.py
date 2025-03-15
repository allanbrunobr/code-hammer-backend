import logging
import requests
from typing import List, Dict, Any, Optional
from .api_client import APIClient

logger = logging.getLogger(__name__)

class GitHubClient:
    """
    Cliente para interação com a API do GitHub.
    """
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
    def get_open_pull_requests(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """
        Busca todos os pull requests abertos de um repositório.
        
        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            
        Returns:
            List[Dict[str, Any]]: Lista de pull requests
        """
        try:
            logger.info(f"[GITHUB-CLIENT] Buscando PRs abertos para {owner}/{repo}")
            
            url = f'{self.base_url}/repos/{owner}/{repo}/pulls'
            params = {'state': 'open'}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            pull_requests = response.json()
            
            # Formatar os dados dos PRs
            formatted_prs = []
            for pr in pull_requests:
                formatted_prs.append({
                    'number': pr['number'],
                    'title': pr['title'],
                    'author': pr['user']['login'],
                    'created_at': pr['created_at'],
                    'updated_at': pr['updated_at'],
                    'status': 'open',
                    'url': pr['html_url']
                })
                
            logger.info(f"[GITHUB-CLIENT] Encontrados {len(formatted_prs)} PRs abertos")
            return formatted_prs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[GITHUB-CLIENT] Erro ao buscar PRs: {str(e)}")
            raise Exception(f"Erro ao buscar pull requests: {str(e)}")
