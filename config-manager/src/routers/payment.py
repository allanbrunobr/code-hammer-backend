"""
Router para gerenciamento de pagamentos via Stripe.
Este módulo expõe as APIs para checkout, portal do cliente e webhooks.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header, Response, status
from fastapi.responses import RedirectResponse
from typing import Dict, Optional, Any
from uuid import UUID
import asyncio
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.middleware.webhook_validator import validate_stripe_webhook

from ..adapters.dtos import (
    CheckoutSessionCreateDTO,
    CheckoutSessionResponseDTO,
    CustomerPortalSessionDTO,
    StripeWebhookDTO,
    SubscriptionUpdateDTO,
)
from ..services.payment import PaymentService

payment_router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    responses={404: {"description": "Not found"}},
)

@payment_router.post("/checkout", response_model=CheckoutSessionResponseDTO)
async def create_checkout_session(
    request: Request,
    checkout_data: CheckoutSessionCreateDTO,
    db: Session = Depends(get_db)
):
    """
    Cria uma sessão de checkout do Stripe para um plano específico.

    Args:
        checkout_data: Dados para criação da sessão de checkout.

    Returns:
        CheckoutSessionResponseDTO: URL da sessão de checkout e ID da sessão.
    """
    payment_service = PaymentService(db=db)
    result = await payment_service.create_checkout_session(checkout_data)
    return result

@payment_router.get("/portal/{user_id}", response_model=CustomerPortalSessionDTO)
async def create_customer_portal_session(
    request: Request,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Cria uma sessão do portal do cliente do Stripe para gerenciar assinaturas.

    Args:
        user_id: ID do usuário.

    Returns:
        CustomerPortalSessionDTO: URL do portal do cliente.
    """
    payment_service = PaymentService(db=db)
    result = await payment_service.create_customer_portal_session(user_id)
    return result

@payment_router.post("/webhook", status_code=200)
async def handle_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
    db: Session = Depends(get_db)
):
    """
    Endpoint para receber eventos do Stripe via webhook.

    Args:
        request: Objeto da requisição.
        stripe_signature: Assinatura do webhook enviada pelo Stripe.

    Returns:
        dict: Resposta indicando o status do processamento.
    """
    # Lê o conteúdo raw da requisição
    payload = await request.body()

    # Cria o DTO para processamento do webhook
    webhook_data = StripeWebhookDTO(
        signature=stripe_signature,
        payload=payload.decode("utf-8"),
    )

    # Processa o webhook
    payment_service = PaymentService(db=db)
    result = await payment_service.handle_webhook(webhook_data)

    return result
