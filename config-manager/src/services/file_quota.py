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
        
        # Calcular arquivos avaliados: total do plano - quota restante
        evaluated_files = plan.file_limit - subscription.remaining_file_quota
        
        # Se estiver fazendo uma simulação de análise, adicionar os arquivos do PR atual
        if pr_file_count > 0:
            evaluated_files += pr_file_count
        
        # Arquivos disponíveis: quota restante - arquivos do PR atual
        available_files = max(0, subscription.remaining_file_quota - pr_file_count)
        
        # Registrar os cálculos no log para diagnóstico
        print(f"Cálculo de quota do usuário {user_id}:")
        print(f"  - Plano: {plan.name}, limite total: {plan.file_limit}")
        print(f"  - Quota restante no banco: {subscription.remaining_file_quota}")
        print(f"  - Arquivos do PR atual: {pr_file_count}")
        print(f"  - Arquivos já avaliados: {evaluated_files}")
        print(f"  - Arquivos disponíveis: {available_files}")
        
        return {
            "evaluated_files": evaluated_files,
            "available_files": available_files,
            "remaining_file_quota": subscription.remaining_file_quota,
            "plan_file_limit": plan.file_limit
        }
    
    def update_user_file_quota(self, db: Session, user_id: UUID, pr_file_count: int) -> Dict:
        """
        Atualiza a quota de arquivos do usuário após a análise de um PR.
        Diminui o valor de remaining_file_quota conforme o número de arquivos analisados.
        
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
        
        # Lógica correta: Diminuir a quota restante pelo número de arquivos analisados
        # Garante que não fique negativa
        updated_remaining = max(0, subscription.remaining_file_quota - pr_file_count)
        
        # Registrar a atualização no log para diagnóstico
        print(f"Atualizando quota do usuário {user_id}:")
        print(f"  - Valor anterior: {subscription.remaining_file_quota}")
        print(f"  - Arquivos analisados: {pr_file_count}")
        print(f"  - Novo valor: {updated_remaining}")
        
        # Atualizar o valor no banco de dados
        subscription.remaining_file_quota = updated_remaining
        
        # Salvar as alterações na assinatura usando um dicionário com os campos a atualizar
        update_data = {"remaining_file_quota": updated_remaining}
        updated_subscription = self.subscription_repository.update_subscription(
            db, 
            subscription.id, 
            update_data
        )
        
        # Verificar se a atualização foi bem-sucedida
        if not updated_subscription:
            raise HTTPException(status_code=500, detail="Falha ao atualizar a quota de arquivos")
        
        # Calcular a quantidade de arquivos avaliados (total - restantes)
        evaluated_files = plan.file_limit - updated_subscription.remaining_file_quota
        
        # Calcular a quantidade de arquivos disponíveis (restantes)
        available_files = updated_subscription.remaining_file_quota
        
        return {
            "evaluated_files": evaluated_files,
            "available_files": available_files,
            "remaining_file_quota": updated_subscription.remaining_file_quota,
            "plan_file_limit": plan.file_limit
        }
