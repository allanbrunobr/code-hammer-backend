import logging
import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from uuid import UUID
from urllib.parse import unquote

from ..adapters.dtos import IntegrationDTO, IntegrationCreateDTO
from ..repositories import IntegrationRepository
from ..utils.environment import Environment

class IntegrationService:
    def __init__(self):
        self.repository = IntegrationRepository()

    def get_integration(self, db: Session, integration_id: UUID) -> IntegrationDTO:
        integration = self.repository.get_integration_by_id(db, integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        return integration

    def create_integration(self, db: Session, integration_data: IntegrationCreateDTO) -> IntegrationDTO:
        try:
            logging.info(f"Entering create_integration with data: {integration_data}")
            new_integration = self.repository.create_integration(db, integration_data)
            logging.info(f"Exiting create_integration with integration: {new_integration}")
            return new_integration
        except Exception as e:
            logging.error(f"Error creating integration: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating integration: {str(e)}"
            )

    def update_integration(self, db: Session, integration_id: UUID, integration_data: IntegrationCreateDTO) -> IntegrationDTO:
        updated_integration = self.repository.update_integration(db, integration_id, integration_data)
        if not updated_integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        return updated_integration

    def delete_integration(self, db: Session, integration_id: UUID) -> IntegrationDTO:
        deleted_integration = self.repository.delete_integration(db, integration_id)
        if not deleted_integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        return deleted_integration

    def list_integrations(self, db: Session, user_id: Optional[UUID] = None) -> List[IntegrationDTO]:
        try:
            return self.repository.list_integrations(db, user_id)
        except Exception as e:
            logging.error(f"Error listing integrations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing integrations: {str(e)}")

    def get_open_pr(self, db: Session, repository_url: str, integration_id: UUID) -> Optional[dict]:
        try:
            logging.info("==================== DEBUG GET OPEN PR SERVICE ====================")
            logging.info(f"Repository URL: {repository_url}")
            logging.info(f"Integration ID: {integration_id}")
            logging.info(f"Tipo do Integration ID: {type(integration_id)}")
            
            # Buscar a integração diretamente pelo ID
            integration = self.repository.get_integration_by_id(db, integration_id)
            if not integration:
                logging.error(f"❌ Integração não encontrada com ID: {integration_id}")
                return None
                
            # Extract owner and repo from URL
            repository_url = unquote(repository_url)
            parts = repository_url.replace("https://", "").replace("http://", "").split("/")
            if len(parts) < 2:
                logging.error(f"Invalid repository URL format: {repository_url}")
                return None
                
            # Se a URL começa com github.com, remover
            if parts[0] == "github.com" or parts[0] == "www.github.com":
                parts = parts[1:]
                
            owner = parts[0]
            repo = parts[1]
            logging.info(f"Owner extraído: {owner}")
            logging.info(f"Repo extraído: {repo}")
            
            # Usar a API do GitHub para buscar PRs abertos
            github_api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            logging.info(f"URL da API do GitHub: {github_api_url}")
            
            token = integration.repository_token
            masked_token = f"{token[:4]}...{token[-4:]}" if token else "None"
            logging.info(f"Token da integração (mascarado): {masked_token}")
            
            headers = {
                "Authorization": f"token {integration.repository_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            logging.info("Headers da requisição:")
            for key, value in headers.items():
                if key.lower() == "authorization":
                    logging.info(f"  {key}: token {value.split(' ')[-1][:4]}...")
                else:
                    logging.info(f"  {key}: {value}")
            
            logging.info("Fazendo requisição para a API do GitHub...")
            response = requests.get(github_api_url, headers=headers)
            
            logging.info(f"Status code da resposta: {response.status_code}")
            if response.status_code == 200:
                prs = response.json()
                if prs:
                    # Pegar o PR mais recente
                    pr = prs[0]
                    pr_info = {
                        "number": pr["number"],
                        "title": pr["title"],
                        "html_url": pr["html_url"]
                    }
                    logging.info(f"✅ PR encontrado: {pr_info}")
                    logging.info("==================== FIM DEBUG ====================")
                    return pr_info
                else:
                    logging.info("❌ Nenhum PR aberto encontrado")
                    logging.info("==================== FIM DEBUG ====================")
                    return None
            else:
                logging.error(f"❌ Erro na API do GitHub: {response.status_code}")
                logging.error(f"Resposta: {response.text}")
                logging.info("==================== FIM DEBUG ====================")
                return None
            
        except Exception as e:
            logging.error(f"❌ Erro ao verificar PRs abertos: {str(e)}")
            logging.info("==================== FIM DEBUG ====================")
            return None
