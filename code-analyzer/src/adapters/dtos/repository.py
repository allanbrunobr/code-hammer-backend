from enum import Enum
from typing import List, Any, Optional
from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)

class TypeRepositoryEnum(str, Enum):
    GITHUB = 'Github'
    GITLAB = 'Gitlab'
    AZURE = 'Azure'
    BITBUCKET = 'Bitbucket'


class RepositoryDTO(BaseModel):
    type: TypeRepositoryEnum
    owner: Optional[str] = None
    repo: Optional[str] = None
    repository_url: Optional[str] = None
    pull_request_number: Optional[int] = None
    project_id: Optional[str] = None
    repo_slug: Optional[str] = None
    pull_request_id: Optional[str] = None
    workspace: Optional[str] = None

    @field_validator('pull_request_number', mode='before')
    @classmethod
    def convert_pull_request_number(cls, v):
        logger.info(f"[REPO-DTO] Convertendo pull_request_number. Valor recebido: {v} (tipo: {type(v)})")
        if v is None:
            logger.info("[REPO-DTO] pull_request_number é None")
            return None
        try:
            converted = int(v)
            logger.info(f"[REPO-DTO] pull_request_number convertido para: {converted}")
            return converted
        except (ValueError, TypeError) as e:
            logger.error(f"[REPO-DTO] Erro ao converter pull_request_number: {str(e)}")
            raise ValueError(f"Pull request number deve ser um número válido, recebido: {v}")


