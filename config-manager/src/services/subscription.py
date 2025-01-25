from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from uuid import UUID

from ..adapters.dtos import SubscriptionCreateDTO, SubscriptionDTO
from ..repositories import SubscriptionRepository


class SubscriptionService:
    def __init__(self):
        self.repository = SubscriptionRepository()

    def get_subscription(self, db: Session, subscription_id: UUID) -> SubscriptionDTO:
        subscription = self.repository.get_subscription_by_id(db, subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription

    def create_subscription(self, db: Session, subscription_data: SubscriptionCreateDTO) -> SubscriptionDTO:
        new_subscription = self.repository.create_subscription(db, subscription_data)
        return new_subscription

    def update_subscription(self, db: Session, subscription_id: UUID, subscription_data: SubscriptionCreateDTO) -> SubscriptionDTO:
        updated_subscription = self.repository.update_subscription(db, subscription_id, subscription_data)
        if not updated_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return updated_subscription

    def delete_subscription(self, db: Session, subscription_id: UUID) -> SubscriptionDTO:
        deleted_subscription = self.repository.delete_subscription(db, subscription_id)
        if not deleted_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return deleted_subscription

    def list_subscriptions(self, db: Session) -> List[SubscriptionDTO]:
        return self.repository.list_subscriptions(db)
