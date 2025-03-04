"""
Middleware para validação de webhooks.
Este módulo contém funções para validar os webhooks do Stripe.
"""
import logging
from fastapi import Request, HTTPException, status
from ..payment.stripe_client import verify_webhook_signature

# Configurando o logger
logger = logging.getLogger(__name__)

async def validate_stripe_webhook(request: Request, stripe_signature: str):
    """
    Valida a assinatura de um webhook do Stripe.
    
    Args:
        request: Objeto da requisição.
        stripe_signature: Assinatura do webhook enviada pelo Stripe.
        
    Raises:
        HTTPException: Se a assinatura for inválida.
    """
    try:
        # Lê o conteúdo raw da requisição
        payload = await request.body()
        
        # Verifica a assinatura do webhook
        verify_webhook_signature(
            payload=payload.decode("utf-8"),
            signature=stripe_signature
        )
        
        # Se chegou aqui, a assinatura é válida
        logger.info("Webhook do Stripe validado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro na validação do webhook do Stripe: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assinatura do webhook inválida"
        )
