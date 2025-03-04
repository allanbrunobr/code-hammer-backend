from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from ..domain import Subscription
from ..adapters.dtos import SubscriptionCreateDTO

class SubscriptionRepository:
    def get_subscription(self, db: Session, subscription_id: UUID) -> Optional[Subscription]:
        """
        Busca uma assinatura pelo ID.
        
        Args:
            db: Sessão do banco de dados.
            subscription_id: ID da assinatura.
            
        Returns:
            Optional[Subscription]: A assinatura encontrada, ou None se não encontrada.
        """
        return db.query(Subscription).filter(Subscription.id == subscription_id).first()

    def get_subscription_by_id(self, db: Session, subscription_id: UUID) -> Optional[Subscription]:
        """
        Alias para get_subscription para compatibilidade.
        """
        return self.get_subscription(db, subscription_id)

    def get_subscription_by_user_id(self, db: Session, user_id: UUID) -> Optional[Subscription]:
        """
        Busca uma assinatura pelo ID do usuário.
        
        Args:
            db: Sessão do banco de dados.
            user_id: ID do usuário.
            
        Returns:
            Optional[Subscription]: A assinatura encontrada, ou None se não encontrada.
        """
        return db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    def get_subscription_by_stripe_id(self, db: Session, stripe_subscription_id: str) -> Optional[Subscription]:
        """
        Busca uma assinatura pelo ID da assinatura no Stripe.
        
        Args:
            db: Sessão do banco de dados.
            stripe_subscription_id: ID da assinatura no Stripe.
            
        Returns:
            Optional[Subscription]: A assinatura encontrada, ou None se não encontrada.
        """
        return db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_subscription_id).first()

    def list_subscriptions(self, db: Session) -> List[Subscription]:
        """
        Lista todas as assinaturas.
        
        Args:
            db: Sessão do banco de dados.
            
        Returns:
            List[Subscription]: Lista de assinaturas.
        """
        return db.query(Subscription).all()

    def create_subscription(self, db: Session, subscription_data) -> Subscription:
        """
        Cria uma nova assinatura.
        
        Args:
            db: Sessão do banco de dados.
            subscription_data: Dados da assinatura a ser criada (DTO ou dicionário).
            
        Returns:
            Subscription: A assinatura criada.
        """
        # Converter para dicionário se for um DTO
        if hasattr(subscription_data, 'dict'):
            data_dict = subscription_data.dict()
        else:
            data_dict = subscription_data
        
        # Criar a assinatura
        new_subscription = Subscription(**data_dict)
        db.add(new_subscription)
        db.commit()
        db.refresh(new_subscription)
        return new_subscription

    def update_subscription(self, db: Session, subscription_id: UUID, subscription_data) -> Optional[Subscription]:
        """
        Atualiza uma assinatura existente.
        
        Args:
            db: Sessão do banco de dados
            subscription_id: ID da assinatura a ser atualizada
            subscription_data: Dados para atualização, pode ser DTO, objeto Subscription ou dicionário
            
        Returns:
            Optional[Subscription]: Assinatura atualizada, ou None se não encontrada
        """
        subscription = self.get_subscription_by_id(db, subscription_id)
        if subscription:
            # Determinar como processar os dados de atualização
            if hasattr(subscription_data, 'dict'):
                # É um DTO, usar o método dict()
                data_dict = subscription_data.dict(exclude_unset=True)
            elif isinstance(subscription_data, Subscription):
                # É um objeto Subscription, converter para dicionário
                data_dict = subscription_data.__dict__
                # Remover atributos SQLAlchemy que não queremos atualizar
                data_dict.pop('_sa_instance_state', None)
            else:
                # É um dicionário ou outro objeto
                data_dict = subscription_data
                
            # Atualizar os atributos
            for key, value in data_dict.items():
                # Pular atributos internos ou privados
                if not key.startswith('_'):
                    setattr(subscription, key, value)
                
            db.commit()
            db.refresh(subscription)
        return subscription

    def delete_subscription(self, db: Session, subscription_id: UUID) -> Optional[Subscription]:
        """
        Exclui uma assinatura pelo ID.
        
        Args:
            db: Sessão do banco de dados.
            subscription_id: ID da assinatura a ser excluída.
            
        Returns:
            Optional[Subscription]: A assinatura excluída, ou None se não encontrada.
        """
        subscription = self.get_subscription_by_id(db, subscription_id)
        if subscription:
            db.delete(subscription)
            db.commit()
        return subscription
