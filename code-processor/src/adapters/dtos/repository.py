from enum import Enum
from typing import List, Any, Optional
from pydantic import BaseModel


class TypeRepositoryEnum(str, Enum):
    GITHUB = 'Github'
    GITLAB = 'Gitlab'
    AZURE = 'Azure'
    BITBUCKET = 'Bitbucket'


class RepositoryDTO(BaseModel):
    type: TypeRepositoryEnum
    token: str = None
    owner: Optional[str] = None
    repo: Optional[str] = None
    pull_request_number: Optional[int] = None
    project_id: Optional[str] = None
    repo_slug: Optional[str] = None
    pull_request_id: Optional[str] = None
    workspace: Optional[str] = None


