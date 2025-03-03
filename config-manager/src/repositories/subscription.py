from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from ..domain import Subscription
from ..adapters.dtos import SubscriptionCreateDTO

class SubscriptionRepository:
    def get_subscription_by_id(self, db: Session, subscription_id: UUID) -> Optional[Subscription]:
        return db.query(Subscription).filter(Subscription.id == subscription_id).first()

    def get_subscription_by_user_id(self, db: Session, user_id: UUID) -> Optional[Subscription]:
        return db.query(Subscription).filter(Subscription.user_id == user_id).first()

    def list_subscriptions(self, db: Session) -> List[Subscription]:
        return db.query(Subscription).all()

    def create_subscription(self, db: Session, subscription_data: SubscriptionCreateDTO) -> Subscription:
        new_subscription = Subscription(**subscription_data.dict())
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
            subscription_data: Dados para atualização, pode ser DTO ou dicionário
            
        Returns:
            Optional[Subscription]: Assinatura atualizada, ou None se não encontrada
        """
        subscription = self.get_subscription_by_id(db, subscription_id)
        if subscription:
            # Determinar se estamos lidando com um DTO ou um dicionário
            if hasattr(subscription_data, 'dict'):
                # É um DTO, usar o método dict()
                data_dict = subscription_data.dict(exclude_unset=True)
            else:
                # É um dicionário simples
                data_dict = subscription_data
                
            # Atualizar os atributos
            for key, value in data_dict.items():
                setattr(subscription, key, value)
                
            db.commit()
            db.refresh(subscription)
        return subscription

    def delete_subscription(self, db: Session, subscription_id: UUID) -> Optional[Subscription]:
        subscription = self.get_subscription_by_id(db, subscription_id)
        if subscription:
            db.delete(subscription)
            db.commit()
        return subscription
