from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import Optional, Dict

from ..adapters.http_client import ConfigManagerClient
from ..services.auth import get_user_id_from_token

file_quota_router = APIRouter(
    prefix="/api/v1/file-quotas",
    tags=["File Quotas"],
)

@file_quota_router.get("/info")
async def get_file_quota_info(
    pr_file_count: int = 0,
    token: str = Depends(get_user_id_from_token)
):
    """
    Retorna informações sobre a quota de arquivos do usuário logado.
    
    Args:
        pr_file_count: Número de arquivos no PR que está sendo analisado
        token: Token de autenticação do usuário
        
    Returns:
        Dict: Informações sobre a quota de arquivos
    """
    try:
        # Obter o ID do usuário a partir do token
        user_id = token  # Assumindo que o get_user_id_from_token retorna o ID do usuário
        
        # Buscar as informações de quota de arquivos
        quota_info = ConfigManagerClient.get_file_quota(user_id, pr_file_count)
        
        return {
            "evaluated_files": quota_info.get("evaluated_files", 0),
            "available_files": quota_info.get("available_files", 0)
        }
    except Exception as e:
        logging.error(f"Error fetching file quota info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@file_quota_router.post("/update")
async def update_file_quota(
    pr_file_count: int,
    token: str = Depends(get_user_id_from_token)
) -> Dict:
    """
    Atualiza a quota de arquivos do usuário após a análise de um PR.
    
    Args:
        pr_file_count: Número de arquivos no PR que foi analisado
        token: Token de autenticação do usuário
        
    Returns:
        Dict: Informações atualizadas sobre a quota de arquivos
    """
    try:
        # Obter o ID do usuário a partir do token
        user_id = token  # Assumindo que o get_user_id_from_token retorna o ID do usuário
        
        # Atualizar a quota de arquivos
        updated_quota = ConfigManagerClient.update_file_quota(user_id, pr_file_count)
        
        if not updated_quota:
            raise HTTPException(status_code=500, detail="Falha ao atualizar a quota de arquivos")
        
        return {
            "evaluated_files": updated_quota.get("evaluated_files", 0),
            "available_files": updated_quota.get("available_files", 0)
        }
    except Exception as e:
        logging.error(f"Error updating file quota: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@file_quota_router.get("/diagnostics/quota")
async def get_diagnostics_quota(
    pr_file_count: int = 0,
    token: str = Depends(get_user_id_from_token)
) -> Dict:
    """
    Retorna informações de diagnóstico sobre a quota de arquivos do usuário.
    
    Args:
        pr_file_count: Número de arquivos no PR que está sendo analisado
        token: Token de autenticação do usuário
        
    Returns:
        Dict: Informações de diagnóstico sobre a quota de arquivos
    """
    try:
        # Obter o ID do usuário a partir do token
        user_id = token  # Assumindo que o get_user_id_from_token retorna o ID do usuário
        
        # Buscar as informações de quota de arquivos
        quota_info = ConfigManagerClient.get_file_quota(user_id, pr_file_count)
        
        if not quota_info:
            # Fornecer valores padrão se não houver informações
            return {
                "evaluated_files": 0,
                "available_files": 25,  # Valor padrão
                "diagnostics": {
                    "status": "default_values",
                    "message": "Usando valores padrão pois não foi possível obter dados reais do banco"
                }
            }
        
        return {
            "evaluated_files": quota_info.get("evaluated_files", 0),
            "available_files": quota_info.get("available_files", 0),
            "diagnostics": {
                "status": "success",
                "message": "Dados obtidos com sucesso"
            }
        }
    except Exception as e:
        logging.error(f"Erro ao buscar dados reais do banco: {str(e)}")
        # Em vez de levantar uma exceção, retornar valores padrão com diagnóstico
        return {
            "evaluated_files": 0,
            "available_files": 25,
            "diagnostics": {
                "status": "error",
                "message": f"Erro ao buscar dados reais do banco: {str(e)}"
            }
        }

@file_quota_router.get("/current-quota")
async def get_current_quota(
    token: str = Depends(get_user_id_from_token)
) -> Dict:
    """
    Retorna informações atuais sobre a quota de arquivos do usuário logado,
    sem considerar arquivos de um novo PR.
    
    Este endpoint é útil para exibir a quantidade de arquivos utilizados
    e disponíveis no momento, para mostrar ao usuário antes de iniciar uma análise.
    
    Args:
        token: Token de autenticação do usuário
        
    Returns:
        Dict: Informações sobre a quota atual de arquivos
            - evaluated_files: Quantidade de arquivos já avaliados
            - available_files: Quantidade de arquivos disponíveis
    """
    try:
        # Obter o ID do usuário a partir do token
        user_id = token  # Assumindo que o get_user_id_from_token retorna o ID do usuário
        
        # Buscar as informações de quota de arquivos atual
        quota_info = ConfigManagerClient.get_quota_info(user_id)
        
        if not quota_info:
            # Fornecer valores padrão se não houver informações
            return {
                "evaluated_files": 0,
                "available_files": 25  # Valor padrão
            }
        
        return {
            "evaluated_files": quota_info.get("evaluated_files", 0),
            "available_files": quota_info.get("available_files", 0)
        }
    except Exception as e:
        logging.error(f"Error fetching current file quota: {str(e)}")
        # Em vez de levantar uma exceção, retornar valores padrão
        return {
            "evaluated_files": 0,
            "available_files": 25
        }
