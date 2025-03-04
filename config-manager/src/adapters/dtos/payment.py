"""
DTOs (Data Transfer Objects) para funcionalidades de pagamento.
Estes DTOs são usados para transferir dados entre as camadas da aplicação.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class PaymentMethodDTO(BaseModel):
    """DTO para métodos de pagamento."""
    id: str
    type: str
    last4: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    brand: Optional[str] = None
    
class CheckoutSessionCreateDTO(BaseModel):
    """DTO para criação de sessão de checkout."""
    plan_id: UUID
    period_id: Optional[UUID] = None
    success_url: str
    cancel_url: str
    user_id: UUID
    
class CheckoutSessionResponseDTO(BaseModel):
    """DTO para resposta de sessão de checkout."""
    checkout_url: str
    session_id: str
    
class SubscriptionUpdateDTO(BaseModel):
    """DTO para atualização de assinatura."""
    auto_renew: Optional[bool] = None
    plan_id: Optional[UUID] = None
    
class CustomerPortalSessionDTO(BaseModel):
    """DTO para sessão do portal do cliente."""
    portal_url: str
    
class StripeWebhookDTO(BaseModel):
    """DTO para webhook do Stripe."""
    signature: str
    payload: str
    
class InvoiceDTO(BaseModel):
    """DTO para faturas."""
    id: str
    amount_due: int
    amount_paid: int
    currency: str
    status: str
    hosted_invoice_url: Optional[str] = None
    payment_intent_id: Optional[str] = None
    created: int
    subscription_id: Optional[str] = None
    customer_id: str
    
class PaymentIntentDTO(BaseModel):
    """DTO para intenções de pagamento."""
    id: str
    amount: int
    currency: str
    status: str
    payment_method: Optional[str] = None
    created: int
    
class StripeEventDTO(BaseModel):
    """DTO para eventos do Stripe."""
    id: str
    type: str
    created: int
    data: dict
