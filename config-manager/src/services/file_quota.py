from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Dict
from uuid import UUID

from ..repositories import SubscriptionRepository, PlanRepository


class FileQuotaService:
    def __init__(self):
        self.subscription_repository = SubscriptionRepository()
        self.plan_repository = PlanRepository()
    
    def get_user_file_quota(self, db: Session, user_id: UUID, pr_file_count: int = 0) -> Dict:
        """
        Retorna informações sobre a quota de arquivos do usuário.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            pr_file_count: Número de arquivos no PR que está sendo analisado
            
        Returns:
            Dict: Dicionário contendo as informações de quota de arquivos
        """
        # Buscar a assinatura do usuário
        subscription = self.subscription_repository.get_subscription_by_user_id(db, user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Assinatura não encontrada para este usuário")
        
        # Buscar o plano associado à assinatura
        plan = self.plan_repository.get_plan_by_id(db, subscription.plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plano não encontrado")
        
        # Calcular a quantidade de arquivos avaliados
        evaluated_files = 0
        if subscription.remaining_file_quota == 0:
            # Primeira vez usando, apenas conta os arquivos do PR atual
            evaluated_files = pr_file_count
        else:
            # Já houve uso anterior, soma os arquivos já usados com os do PR atual
            evaluated_files = subscription.remaining_file_quota + pr_file_count
        
        # Calcular a quantidade de arquivos disponíveis
        available_files = plan.file_limit - subscription.remaining_file_quota
        
        return {
            "evaluated_files": evaluated_files,
            "available_files": available_files,
            "remaining_file_quota": subscription.remaining_file_quota,
            "plan_file_limit": plan.file_limit
        }
    
    def update_user_file_quota(self, db: Session, user_id: UUID, pr_file_count: int) -> Dict:
        """
        Atualiza a quota de arquivos do usuário após a análise de um PR.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            pr_file_count: Número de arquivos no PR que foi analisado
            
        Returns:
            Dict: Dicionário contendo as informações atualizadas de quota de arquivos
        """
        # Buscar a assinatura do usuário
        subscription = self.subscription_repository.get_subscription_by_user_id(db, user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Assinatura não encontrada para este usuário")
        
        # Buscar o plano associado à assinatura
        plan = self.plan_repository.get_plan_by_id(db, subscription.plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plano não encontrado")
        
        # Atualizar a quota de arquivos restantes
        if subscription.remaining_file_quota == 0:
            # Primeira vez, define como o número de arquivos do PR
            subscription.remaining_file_quota = pr_file_count
        else:
            # Já houve uso anterior, soma os arquivos do PR
            subscription.remaining_file_quota += pr_file_count
        
        # Salvar as alterações na assinatura
        updated_subscription = self.subscription_repository.update_subscription(
            db, 
            subscription.id, 
            {"remaining_file_quota": subscription.remaining_file_quota}
        )
        
        # Calcular a quantidade de arquivos avaliados (agora já atualizada)
        evaluated_files = updated_subscription.remaining_file_quota
        
        # Calcular a quantidade de arquivos disponíveis
        available_files = plan.file_limit - updated_subscription.remaining_file_quota
        
        return {
            "evaluated_files": evaluated_files,
            "available_files": available_files,
            "remaining_file_quota": updated_subscription.remaining_file_quota,
            "plan_file_limit": plan.file_limit
        }
