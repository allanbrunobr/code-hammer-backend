from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..adapters.dtos import SubscriptionDTO, SubscriptionCreateDTO
from ..services import SubscriptionService
from ..core.db.database import get_db

subscription_router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)

subscription_service = SubscriptionService()

@subscription_router.get("/", response_model=List[SubscriptionDTO])
def list_subscriptions(db: Session = Depends(get_db)):
    return subscription_service.list_subscriptions(db)

@subscription_router.post("/", response_model=SubscriptionDTO)
def create_subscription_endpoint(subscription: SubscriptionCreateDTO, db: Session = Depends(get_db)):
    return subscription_service.create_subscription(db, subscription)

@subscription_router.get("/{subscription_id}", response_model=SubscriptionDTO)
def get_subscription(subscription_id: UUID, db: Session = Depends(get_db)):
    return subscription_service.get_subscription(db, subscription_id)

@subscription_router.put("/{subscription_id}", response_model=SubscriptionDTO)
def update_subscription_endpoint(subscription_id: UUID, subscription: SubscriptionCreateDTO, db: Session = Depends(get_db)):
    return subscription_service.update_subscription(db, subscription_id, subscription)

@subscription_router.delete("/{subscription_id}", response_model=SubscriptionDTO)
def delete_subscription_endpoint(subscription_id: UUID, db: Session = Depends(get_db)):
    return subscription_service.delete_subscription(db, subscription_id)

@subscription_router.get("/current", response_model=SubscriptionDTO)
def get_current_subscription(email: str = None, db: Session = Depends(get_db)):
    # Redireciona para o endpoint de usuário se o email estiver presente
    if email:
        from ..repositories.user import UserRepository
        user_repo = UserRepository()
        try:
            user = user_repo.get_user_by_email(db, email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return subscription_service.get_user_subscription(db, user.id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Email is required")
