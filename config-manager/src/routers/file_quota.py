from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from uuid import UUID

from ..core.db.database import get_db
from ..services.file_quota import FileQuotaService
from ..services.auth import get_current_user
from ..adapters.dtos import UserDTO

file_quota_router = APIRouter(
    prefix="/file-quotas",
    tags=["File Quotas"],
)

file_quota_service = FileQuotaService()

@file_quota_router.get("/user/{user_id}", response_model=Dict)
def get_user_file_quota(
    user_id: UUID, 
    pr_file_count: int = 0,
    db: Session = Depends(get_db),
    current_user: UserDTO = Depends(get_current_user)
):
    """
    Retorna informações sobre a quota de arquivos do usuário,
    incluindo a quantidade de arquivos avaliados e disponíveis.
    
    - Se remaining_file_quota for zero (primeira vez), arquivos avaliados = pr_file_count
    - Se remaining_file_quota for diferente de zero, arquivos avaliados = remaining_file_quota + pr_file_count
    - Arquivos disponíveis = file_limit do plano - remaining_file_quota
    """
    # Verificar se o usuário tem permissão para acessar os dados
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    
    # Buscar as informações de quota de arquivos
    return file_quota_service.get_user_file_quota(db, user_id, pr_file_count)

@file_quota_router.post("/user/{user_id}/update-quota")
def update_user_file_quota(
    user_id: UUID,
    pr_file_count: int,
    db: Session = Depends(get_db),
    current_user: UserDTO = Depends(get_current_user)
):
    """
    Atualiza a quota de arquivos do usuário após a análise de um PR.
    Esta função deve ser chamada quando o usuário solicita uma análise.
    """
    # Verificar se o usuário tem permissão para acessar os dados
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    
    # Atualizar a quota de arquivos
    return file_quota_service.update_user_file_quota(db, user_id, pr_file_count)
