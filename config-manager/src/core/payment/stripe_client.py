"""
Módulo responsável pela integração com a API do Stripe.
Este módulo isola a interação com o Stripe do resto do sistema.
"""
import os
import stripe
import logging
from dotenv import load_dotenv

# Carregando as variáveis de ambiente
load_dotenv()

# Configurando o logger
logger = logging.getLogger(__name__)

# Obtendo as chaves do Stripe a partir das variáveis de ambiente
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Configurando o Stripe com a chave secreta
stripe.api_key = STRIPE_SECRET_KEY

def get_stripe_instance():
    """
    Retorna a instância configurada do cliente do Stripe.
    
    Returns:
        module: A instância configurada do módulo stripe.
    """
    return stripe

def get_webhook_secret():
    """
    Retorna o webhook secret do Stripe.
    
    Returns:
        str: O webhook secret do Stripe.
    """
    return STRIPE_WEBHOOK_SECRET

def create_customer(name, email, metadata=None):
    """
    Cria um novo cliente no Stripe.
    
    Args:
        name (str): Nome do cliente.
        email (str): Email do cliente.
        metadata (dict, optional): Metadados adicionais para o cliente.
        
    Returns:
        stripe.Customer: O objeto do cliente criado.
        
    Raises:
        stripe.error.StripeError: Se ocorrer um erro na API do Stripe.
    """
    logger.info(f"Iniciando criação de customer no Stripe para {email}")
    
    # Verificar se já existe um cliente com esse email
    try:
        existing_customers = stripe.Customer.list(email=email, limit=1)
        if existing_customers and existing_customers.data:
            customer = existing_customers.data[0]
            logger.info(f"Customer já existe no Stripe: {customer.id} para {email}")
            return customer
    except Exception as e:
        logger.warning(f"Erro ao buscar customer existente: {str(e)}. Continuando com criação de novo customer.")
    
    # Criar um novo cliente
    try:
        # Certifique-se de que name não é None
        safe_name = name or email.split('@')[0]
        
        customer = stripe.Customer.create(
            name=safe_name,
            email=email,
            metadata=metadata or {}
        )
        logger.info(f"Cliente criado no Stripe: {customer.id} para {email}")
        return customer
    except stripe.error.StripeError as e:
        logger.error(f"Erro ao criar cliente no Stripe: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao criar cliente no Stripe: {str(e)}")
        raise stripe.error.StripeError(f"Erro inesperado: {str(e)}")

def create_checkout_session(customer_id, price_id, success_url, cancel_url, metadata=None):
    """
    Cria uma sessão de checkout do Stripe para uma assinatura.
    
    Args:
        customer_id (str): ID do cliente no Stripe.
        price_id (str): ID do preço do plano no Stripe.
        success_url (str): URL para redirecionamento em caso de sucesso.
        cancel_url (str): URL para redirecionamento em caso de cancelamento.
        metadata (dict, optional): Metadados adicionais para a sessão.
        
    Returns:
        stripe.checkout.Session: A sessão de checkout criada.
        
    Raises:
        stripe.error.StripeError: Se ocorrer um erro na API do Stripe.
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {}
        )
        logger.info(f"Sessão de checkout criada: {checkout_session.id}")
        return checkout_session
    except stripe.error.StripeError as e:
        logger.error(f"Erro ao criar sessão de checkout: {str(e)}")
        raise

def create_customer_portal_session(customer_id, return_url):
    """
    Cria uma sessão do portal do cliente do Stripe.
    
    Args:
        customer_id (str): ID do cliente no Stripe.
        return_url (str): URL para retorno após o uso do portal.
        
    Returns:
        stripe.billing_portal.Session: A sessão do portal do cliente.
        
    Raises:
        stripe.error.StripeError: Se ocorrer um erro na API do Stripe.
    """
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url
        )
        logger.info(f"Sessão do portal do cliente criada: {portal_session.id}")
        return portal_session
    except stripe.error.StripeError as e:
        logger.error(f"Erro ao criar sessão do portal do cliente: {str(e)}")
        raise

def verify_webhook_signature(payload, signature):
    """
    Verifica a assinatura de um webhook do Stripe.
    
    Args:
        payload (str): O corpo da requisição do webhook.
        signature (str): A assinatura do webhook.
        
    Returns:
        stripe.Event: O evento verificado.
        
    Raises:
        stripe.error.SignatureVerificationError: Se a assinatura for inválida.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"Webhook verificado: {event.id} do tipo {event.type}")
        return event
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Assinatura de webhook inválida: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro ao verificar webhook: {str(e)}")
        raise

def get_subscription(subscription_id):
    """
    Obtém os detalhes de uma assinatura no Stripe.
    
    Args:
        subscription_id (str): ID da assinatura no Stripe.
        
    Returns:
        stripe.Subscription: Os detalhes da assinatura.
        
    Raises:
        stripe.error.StripeError: Se ocorrer um erro na API do Stripe.
    """
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription
    except stripe.error.StripeError as e:
        logger.error(f"Erro ao obter assinatura {subscription_id}: {str(e)}")
        raise

def update_subscription(subscription_id, cancel_at_period_end=None, items=None):
    """
    Atualiza uma assinatura no Stripe.
    
    Args:
        subscription_id (str): ID da assinatura no Stripe.
        cancel_at_period_end (bool, optional): Indica se a assinatura deve ser cancelada no final do período.
        items (list, optional): Lista de itens a serem atualizados na assinatura.
        
    Returns:
        stripe.Subscription: A assinatura atualizada.
        
    Raises:
        stripe.error.StripeError: Se ocorrer um erro na API do Stripe.
    """
    try:
        update_params = {}
        
        if cancel_at_period_end is not None:
            update_params['cancel_at_period_end'] = cancel_at_period_end
            
        if items:
            update_params['items'] = items
            
        if update_params:
            subscription = stripe.Subscription.modify(
                subscription_id,
                **update_params
            )
            logger.info(f"Assinatura {subscription_id} atualizada")
            return subscription
        else:
            logger.warning(f"Nenhum parâmetro fornecido para atualizar a assinatura {subscription_id}")
            return get_subscription(subscription_id)
    except stripe.error.StripeError as e:
        logger.error(f"Erro ao atualizar assinatura {subscription_id}: {str(e)}")
        raise
