import logging

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..adapters.dtos.user import UserDTO, UserCreateDTO, UserUpdateDTO, UserIdDTO, UserEmailQueryDTO
from ..services.user import UserService
from ..services.subscription import SubscriptionService
from ..services.auth import get_current_user
from ..core.db.database import get_db
from fastapi import Query
from sqlalchemy import select, text


user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# Instanciar os serviços
user_service = UserService()
subscription_service = SubscriptionService()


@user_router.get("/me", response_model=UserDTO)
def read_users_me(
    current_user: UserDTO = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return current_user

@user_router.get("/check-email")
def check_email_endpoint(
    email: str = Query(...),
    db: Session = Depends(get_db)
):
    exists = user_service.check_email_exists(db, email)
    return {"exists": exists}

@user_router.get("/by-email", response_model=UserIdDTO)
def get_user_id_by_email_endpoint(
    email: str = Query(...),
    db: Session = Depends(get_db)
):
    email = email.strip()
    logging.info(f"Email after strip: {email}")
    try:
        user_id = user_service.get_user_id_by_email(db, email)
        logging.info(f"get_user_id_by_email_endpoint: Retrieved user_id: {user_id}")
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        return UserIdDTO(userId=user_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logging.error(f"Error in get_user_id_by_email_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@user_router.get("/{user_id}/subscription")
def get_user_subscription_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    try:
        # Consulta SQL que junta as tabelas subscriptions, plans e plan_periods
        # para obter todos os dados necessários
        query = text("""
            SELECT 
                s.id,
                s.status,
                s.start_date,
                s.end_date,
                s.remaining_file_quota,
                s.auto_renew,
                p.id as plan_id,
                p.name as plan_name,
                p.file_limit,
                p.description,
                pp.price,
                pp.currency
            FROM 
                subscriptions s
            JOIN 
                plans p ON s.plan_id = p.id
            LEFT JOIN 
                plan_periods pp ON p.id = pp.plan_id AND pp.period_id = (
                    SELECT id FROM periods WHERE name = 'monthly' LIMIT 1
                )
            WHERE 
                s.user_id = :user_id
            LIMIT 1
        """)
        
        result = db.execute(query, {"user_id": str(user_id)}).fetchone()
        
        if result:
            # Verificar se o preço está disponível
            price = float(result.price) if result.price is not None else 99.90  # Valor padrão se não houver preço
            
            # Consulta para ver quantos pagamentos foram feitos
            payment_query = text("""
                SELECT COUNT(*) as payment_count
                FROM billings
                WHERE user_id = :user_id AND payment_status = 'completed'
            """)
            
            payment_result = db.execute(payment_query, {"user_id": str(user_id)}).fetchone()
            payments_made = payment_result.payment_count if payment_result else 0
            
            # Se for um plano anual, calculamos as parcelas restantes (12 meses - pagamentos feitos)
            remaining_payments = 12 - payments_made if payments_made < 12 else 0
            
            # Construir resposta
            response = {
                "id": str(result.id),
                "status": result.status,
                "plan": result.plan_name,
                "planId": str(result.plan_id),
                "startDate": result.start_date.isoformat() if result.start_date else None,
                "endDate": result.end_date.isoformat() if result.end_date else None,
                "remainingFileQuota": result.remaining_file_quota or result.file_limit,
                "autoRenew": result.auto_renew,
                "description": result.description,
                "price": price,
                "currency": result.currency or "BRL",
                "remainingPayments": remaining_payments
            }
            return response
        
        # Se não encontrar assinatura, verificar se o usuário existe
        user = user_service.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Se o usuário existe mas não tem assinatura, retornar plano gratuito
        free_plan_query = text("""
            SELECT 
                p.id as plan_id,
                p.name as plan_name,
                p.file_limit,
                p.description
            FROM 
                plans p
            WHERE 
                p.name = 'Gratuito'
            LIMIT 1
        """)
        
        free_plan = db.execute(free_plan_query).fetchone()
        
        if free_plan:
            return {
                "status": "active",
                "plan": free_plan.plan_name,
                "planId": str(free_plan.plan_id),
                "startDate": None,
                "endDate": None,
                "remainingFileQuota": free_plan.file_limit,
                "autoRenew": False,
                "description": free_plan.description,
                "price": 0.0,
                "currency": "BRL",
                "remainingPayments": 0
            }
        
        # Fallback padrão
        return {
            "status": "active",
            "plan": "Gratuito",
            "planId": "4fb7a959-cd1d-40f3-a73d-e043604b3f0a",  # ID do plano gratuito
            "startDate": None,
            "endDate": None,
            "remainingFileQuota": 5,  # Limite do plano gratuito
            "autoRenew": False,
            "description": "Plano gratuito com recursos básicos",
            "price": 0.0,
            "currency": "BRL",
            "remainingPayments": 0
        }
        
    except Exception as e:
        logging.error(f"Error in get_user_subscription_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@user_router.get("/", response_model=List[UserDTO])
def list_users_endpoint(
    db: Session = Depends(get_db)
):
    return user_service.list_users(db)

@user_router.post("/", response_model=UserDTO)
def create_user_endpoint(
    user: UserCreateDTO,
    db: Session = Depends(get_db)
):
    return user_service.create_user(db, user)

@user_router.get("/{user_id}", response_model=UserDTO)
def read_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    return user_service.get_user(db, user_id)

@user_router.put("/{user_id}", response_model=UserDTO)
def update_user_endpoint(
    user_id: UUID,
    user: UserUpdateDTO,
    db: Session = Depends(get_db)
):
    return user_service.update_user(db, user_id, user)

@user_router.delete("/{user_id}", response_model=UserDTO)
def delete_user_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    return user_service.delete_user(db, user_id)
