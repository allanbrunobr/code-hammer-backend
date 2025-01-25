from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from ..domain import Subscription
from ..adapters.dtos import SubscriptionCreateDTO

class SubscriptionRepository:
    def get_subscription_by_id(self, db: Session, subscription_id: UUID) -> Optional[Subscription]:
        return db.query(Subscription).filter(Subscription.uuid == subscription_id).first()

    def list_subscriptions(self, db: Session) -> List[Subscription]:
        return db.query(Subscription).all()

    def create_subscription(self, db: Session, subscription_data: SubscriptionCreateDTO) -> Subscription:
        new_subscription = Subscription(**subscription_data.dict())
        db.add(new_subscription)
        db.commit()
        db.refresh(new_subscription)
        return new_subscription

    def update_subscription(self, db: Session, subscription_id: UUID, subscription_data: SubscriptionCreateDTO) -> Optional[Subscription]:
        subscription = self.get_subscription_by_id(db, subscription_id)
        if subscription:
            for key, value in subscription_data.dict(exclude_unset=True).items():
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
