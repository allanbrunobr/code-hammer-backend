"""
Serviço responsável pelo gerenciamento de pagamentos e assinaturas.
Este serviço utiliza o cliente do Stripe para processar pagamentos e gerenciar assinaturas.
"""
import logging
from datetime import datetime
from fastapi import HTTPException
from typing import Optional
import uuid

from ..core.payment.stripe_client import (
    create_customer,
    create_checkout_session,
    create_customer_portal_session,
    get_subscription,
    update_subscription,
    verify_webhook_signature
)
from ..adapters.dtos import (
    CheckoutSessionCreateDTO,
    CheckoutSessionResponseDTO,
    CustomerPortalSessionDTO,
    SubscriptionUpdateDTO,
    StripeWebhookDTO
)
from ..repositories.user import UserRepository
from ..repositories.plan import PlanRepository
from ..repositories.subscription import SubscriptionRepository
from ..repositories.billing import BillingRepository

# Configurando o logger
logger = logging.getLogger(__name__)

class PaymentService:
    """Serviço para gerenciamento de pagamentos e assinaturas."""
    
    def __init__(self, db=None):
        """
        Inicializa o serviço de pagamento.
        
        Args:
            db (Session, optional): Sessão do banco de dados. Se não for fornecida,
                os repositories irão criar suas próprias sessões.
        """
        self.db = db
        self.user_repository = UserRepository()
        self.plan_repository = PlanRepository()
        self.subscription_repository = SubscriptionRepository()
        self.billing_repository = BillingRepository()
    
    async def create_checkout_session(self, checkout_data: CheckoutSessionCreateDTO) -> CheckoutSessionResponseDTO:
        """
        Cria uma sessão de checkout do Stripe para um plano específico.
        
        Args:
            checkout_data: DTO com os dados para criação da sessão de checkout.
            
        Returns:
            CheckoutSessionResponseDTO: DTO com a URL de checkout e o ID da sessão.
            
        Raises:
            HTTPException: Se ocorrer um erro ao criar a sessão de checkout.
        """
        try:
            # Busca o usuário no banco de dados
            user = self.user_repository.get_user_by_id(self.db, checkout_data.user_id)
            if not user:
                logger.error(f"Usuário não encontrado: {checkout_data.user_id}")
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
            # Busca o plano no banco de dados
            plan = self.plan_repository.get_plan_by_id(self.db, checkout_data.plan_id)
            if not plan:
                logger.error(f"Plano não encontrado: {checkout_data.plan_id}")
                raise HTTPException(status_code=404, detail="Plano não encontrado")
            
            # Verifica se o usuário já tem um customer_id no Stripe
            # Tratamento especial para caso de objetos sem o atributo stripe_customer_id
            try:
                stripe_customer_id = user.stripe_customer_id
            except AttributeError:
                stripe_customer_id = None
                logger.warning(f"Objeto User não possui atributo stripe_customer_id: {user.id}")
                
            # Se não tiver, cria um novo customer no Stripe
            if not stripe_customer_id:
                try:
                    logger.info(f"Criando customer no Stripe para usuário {user.id} com email {user.email}")
                    customer = create_customer(
                        name=user.name,
                        email=user.email,
                        metadata={"user_id": str(user.id)}
                    )
                    stripe_customer_id = customer.id
                    
                    # Atualiza o usuário com o ID do customer no Stripe
                    # Usando DTO ao invés do objeto diretamente para evitar problemas de atributos
                    update_data = {"stripe_customer_id": stripe_customer_id}
                    self.user_repository.update_user(self.db, user.id, update_data)
                    logger.info(f"Customer do Stripe criado e associado ao usuário {user.id}: {stripe_customer_id}")
                except Exception as e:
                    logger.error(f"Erro ao criar customer no Stripe: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Erro ao criar customer no Stripe: {str(e)}")
            
            # Obtém o período (se especificado)
            period_id = checkout_data.period_id
            
            # Define o stripe_price_id baseado no plano e período
            stripe_price_id = None
            if period_id:
                # Busca o plan_period correspondente
                plan_period = self.plan_repository.get_plan_period(self.db, plan.id, period_id)
                if not plan_period:
                    logger.error(f"Combinação de plano {plan.id} e período {period_id} não encontrada")
                    raise HTTPException(status_code=404, detail="Combinação de plano e período não encontrada")
                
                # Verifica se o plan_period tem stripe_price_id
                try:
                    stripe_price_id = plan_period.stripe_price_id
                    if not stripe_price_id:
                        logger.error(f"Plan Period não possui stripe_price_id definido: {plan_period.id}")
                        raise HTTPException(status_code=500, detail="Preço do Stripe não configurado para este período de plano")
                except AttributeError:
                    logger.error(f"PlanPeriod não possui atributo stripe_price_id: {plan_period.id}")
                    raise HTTPException(status_code=500, detail="Atributo stripe_price_id não encontrado no modelo PlanPeriod")
            else:
                # Usa o preço padrão do plano (mensal)
                stripe_price_id = plan.stripe_price_id
            
            # Verifica se existe um price_id configurado
            if not stripe_price_id:
                logger.error(f"Preço do Stripe não configurado para o plano {plan.id}")
                raise HTTPException(status_code=500, detail="Preço do Stripe não configurado para este plano")
            
            # Cria a sessão de checkout
            try:
                checkout_session = create_checkout_session(
                    customer_id=stripe_customer_id,
                    price_id=stripe_price_id,
                    success_url=checkout_data.success_url,
                    cancel_url=checkout_data.cancel_url,
                    metadata={
                        "user_id": str(user.id),
                        "plan_id": str(plan.id),
                        "period_id": str(period_id) if period_id else None
                    }
                )
                
                logger.info(f"Sessão de checkout criada: {checkout_session.id} para o usuário {user.id}")
                
                return CheckoutSessionResponseDTO(
                    checkout_url=checkout_session.url,
                    session_id=checkout_session.id
                )
            except Exception as e:
                logger.error(f"Erro ao criar sessão de checkout: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Erro ao criar sessão de checkout: {str(e)}")
                
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar sessão de checkout: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar sessão de checkout: {str(e)}")
    
    async def create_customer_portal_session(self, user_id: uuid.UUID) -> CustomerPortalSessionDTO:
        """
        Cria uma sessão do portal do cliente do Stripe para gerenciar assinaturas.
        
        Args:
            user_id: ID do usuário.
            
        Returns:
            CustomerPortalSessionDTO: DTO com a URL do portal do cliente.
            
        Raises:
            HTTPException: Se ocorrer um erro ao criar a sessão do portal.
        """
        try:
            # Busca o usuário no banco de dados
            user = self.user_repository.get_user_by_id(self.db, user_id)
            if not user:
                logger.error(f"Usuário não encontrado: {user_id}")
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
            # Verifica se o usuário tem um customer_id no Stripe
            try:
                stripe_customer_id = user.stripe_customer_id
                if not stripe_customer_id:
                    logger.error(f"Usuário {user_id} não possui um customer_id no Stripe")
                    raise HTTPException(status_code=400, detail="Usuário não possui uma conta no Stripe")
            except AttributeError:
                logger.error(f"Objeto User não possui atributo stripe_customer_id: {user_id}")
                raise HTTPException(status_code=400, detail="Usuário não possui uma conta no Stripe")
            
            # Cria a sessão do portal do cliente
            try:
                portal_session = create_customer_portal_session(
                    customer_id=stripe_customer_id,
                    return_url=f"{self._get_app_url()}/account/billing"
                )
                
                logger.info(f"Sessão do portal do cliente criada: {portal_session.id} para o usuário {user_id}")
                
                return CustomerPortalSessionDTO(
                    portal_url=portal_session.url
                )
            except Exception as e:
                logger.error(f"Erro ao criar sessão do portal do cliente: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Erro ao criar sessão do portal: {str(e)}")
                
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar sessão do portal: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar sessão do portal: {str(e)}")
    
    async def handle_webhook(self, webhook_data: StripeWebhookDTO):
        """
        Processa webhooks do Stripe para eventos como pagamentos bem-sucedidos,
        atualizações de assinatura, etc.
        
        Args:
            webhook_data: DTO com os dados do webhook.
            
        Returns:
            dict: Resposta indicando o status do processamento.
            
        Raises:
            HTTPException: Se ocorrer um erro ao processar o webhook.
        """
        try:
            # Verifica a assinatura do webhook
            try:
                event = verify_webhook_signature(
                    payload=webhook_data.payload,
                    signature=webhook_data.signature
                )
            except Exception as e:
                logger.error(f"Erro na verificação da assinatura do webhook: {str(e)}")
                raise HTTPException(status_code=400, detail="Assinatura do webhook inválida")
            
            # Processa o evento baseado no tipo
            event_type = event.type
            logger.info(f"Processando evento do Stripe: {event.id} do tipo {event_type}")
            
            # Eventos de checkout
            if event_type == 'checkout.session.completed':
                await self._handle_checkout_completed(event.data.object)
            
            # Eventos de fatura
            elif event_type == 'invoice.payment_succeeded':
                await self._handle_invoice_payment_succeeded(event.data.object)
            elif event_type == 'invoice.payment_failed':
                await self._handle_invoice_payment_failed(event.data.object)
            
            # Eventos de assinatura
            elif event_type == 'customer.subscription.updated':
                await self._handle_subscription_updated(event.data.object)
            elif event_type == 'customer.subscription.deleted':
                await self._handle_subscription_deleted(event.data.object)
            
            # Outros eventos
            else:
                logger.info(f"Evento não processado: {event_type}")
            
            return {"status": "success", "event_type": event_type}
            
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao processar webhook: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao processar webhook: {str(e)}")
    
    async def _handle_checkout_completed(self, checkout_session):
        """
        Processa um evento de checkout.session.completed.
        Cria uma nova assinatura no banco de dados.
        
        Args:
            checkout_session: Objeto da sessão de checkout do Stripe.
        """
        logger.info(f"Processando checkout completado: {checkout_session.id}")
        
        # Extrai metadados
        metadata = checkout_session.metadata or {}
        user_id = metadata.get('user_id')
        plan_id = metadata.get('plan_id')
        
        if not user_id or not plan_id:
            logger.error(f"Metadados incompletos na sessão de checkout: {checkout_session.id}")
            return
        
        # Verifica se já existe uma assinatura para o checkout
        subscription_id = checkout_session.subscription
        if not subscription_id:
            logger.error(f"ID de assinatura ausente na sessão de checkout: {checkout_session.id}")
            return
        
        # Buscar a assinatura criada no Stripe
        try:
            stripe_subscription = get_subscription(subscription_id)
            
            # Obter o plano para ler o file_limit
            plan = self.plan_repository.get_plan_by_id(self.db, plan_id)
            if not plan:
                logger.error(f"Plano {plan_id} não encontrado")
                return
            
            # Criar registro de assinatura no banco de dados
            start_date = datetime.fromtimestamp(stripe_subscription.current_period_start)
            end_date = datetime.fromtimestamp(stripe_subscription.current_period_end)
            
            subscription_data = {
                "id": str(uuid.uuid4()),
                "status": stripe_subscription.status,
                "start_date": start_date,
                "end_date": end_date,
                "auto_renew": not stripe_subscription.cancel_at_period_end,
                "plan_id": plan_id,
                "user_id": user_id,
                "stripe_subscription_id": subscription_id,
                "remaining_file_quota": plan.file_limit
            }
            
            # Verifica se já existe uma assinatura ativa para o usuário
            existing_subscription = self.subscription_repository.get_subscription_by_user_id(self.db, user_id)
            if existing_subscription:
                # Atualiza a assinatura existente
                logger.info(f"Atualizando assinatura existente {existing_subscription.id} para o usuário {user_id}")
                self.subscription_repository.update_subscription(
                    self.db, 
                    existing_subscription.id, 
                    subscription_data
                )
            else:
                # Cria uma nova assinatura
                logger.info(f"Criando nova assinatura para o usuário {user_id}")
                self.subscription_repository.create_subscription(self.db, subscription_data)
            
            logger.info(f"Assinatura processada com sucesso para checkout {checkout_session.id}")
        except Exception as e:
            logger.error(f"Erro ao processar assinatura para checkout {checkout_session.id}: {str(e)}")
    
    async def _handle_invoice_payment_succeeded(self, invoice):
        """
        Processa um evento de invoice.payment_succeeded.
        Atualiza a assinatura e cria um registro de faturamento.
        
        Args:
            invoice: Objeto da fatura do Stripe.
        """
        logger.info(f"Processando pagamento de fatura bem-sucedido: {invoice.id}")
        
        # Obter a assinatura associada à fatura
        subscription_id = invoice.subscription
        if not subscription_id:
            logger.info(f"Fatura {invoice.id} não está associada a uma assinatura")
            return
        
        try:
            # Buscar a assinatura no Stripe
            stripe_subscription = get_subscription(subscription_id)
            
            # Buscar a assinatura no banco de dados
            db_subscription = self.subscription_repository.get_subscription_by_stripe_id(
                self.db, 
                subscription_id
            )
            
            # Se encontrou a assinatura, atualiza as datas
            if db_subscription:
                db_subscription.start_date = datetime.fromtimestamp(
                    stripe_subscription.current_period_start
                )
                db_subscription.end_date = datetime.fromtimestamp(
                    stripe_subscription.current_period_end
                )
                db_subscription.status = stripe_subscription.status
                
                self.subscription_repository.update_subscription(
                    self.db, 
                    db_subscription.id, 
                    db_subscription
                )
                
                logger.info(f"Assinatura {db_subscription.id} atualizada após pagamento de fatura")
            else:
                logger.warning(f"Assinatura com stripe_id {subscription_id} não encontrada no banco de dados")
            
            # Criar registro de pagamento
            billing_data = {
                "id": str(uuid.uuid4()),
                "amount": str(invoice.amount_paid / 100),  # Convertendo centavos para unidades
                "currency": invoice.currency,
                "payment_date": str(invoice.created),
                "payment_method": "card",
                "payment_status": "succeeded",
                "transaction_id": invoice.payment_intent,
                "plan_id": str(db_subscription.plan_id) if db_subscription else None,
                "user_id": db_subscription.user_id if db_subscription else None,
                "stripe_invoice_id": invoice.id,
                "stripe_payment_intent_id": invoice.payment_intent
            }
            
            self.billing_repository.create_billing(self.db, billing_data)
            logger.info(f"Registro de faturamento criado para fatura {invoice.id}")
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento de fatura {invoice.id}: {str(e)}")
    
    async def _handle_invoice_payment_failed(self, invoice):
        """
        Processa um evento de invoice.payment_failed.
        Atualiza o status da assinatura e cria um registro de faturamento.
        
        Args:
            invoice: Objeto da fatura do Stripe.
        """
        logger.info(f"Processando falha de pagamento de fatura: {invoice.id}")
        
        # Obter a assinatura associada à fatura
        subscription_id = invoice.subscription
        if not subscription_id:
            logger.info(f"Fatura {invoice.id} não está associada a uma assinatura")
            return
        
        try:
            # Buscar a assinatura no banco de dados
            db_subscription = self.subscription_repository.get_subscription_by_stripe_id(
                self.db, 
                subscription_id
            )
            
            # Se encontrou a assinatura, atualiza o status
            if db_subscription:
                db_subscription.status = "past_due"
                
                self.subscription_repository.update_subscription(
                    self.db, 
                    db_subscription.id, 
                    db_subscription
                )
                
                logger.info(f"Status da assinatura {db_subscription.id} atualizado para 'past_due'")
            else:
                logger.warning(f"Assinatura com stripe_id {subscription_id} não encontrada no banco de dados")
            
            # Criar registro de pagamento com falha
            billing_data = {
                "id": str(uuid.uuid4()),
                "amount": str(invoice.amount_due / 100),
                "currency": invoice.currency,
                "payment_date": str(invoice.created),
                "payment_method": "card",
                "payment_status": "failed",
                "transaction_id": invoice.payment_intent,
                "plan_id": str(db_subscription.plan_id) if db_subscription else None,
                "user_id": db_subscription.user_id if db_subscription else None,
                "stripe_invoice_id": invoice.id,
                "stripe_payment_intent_id": invoice.payment_intent
            }
            
            self.billing_repository.create_billing(self.db, billing_data)
            logger.info(f"Registro de faturamento com falha criado para fatura {invoice.id}")
            
        except Exception as e:
            logger.error(f"Erro ao processar falha de pagamento de fatura {invoice.id}: {str(e)}")
    
    async def _handle_subscription_updated(self, subscription):
        """
        Processa um evento de customer.subscription.updated.
        Atualiza os detalhes da assinatura no banco de dados.
        
        Args:
            subscription: Objeto da assinatura do Stripe.
        """
        logger.info(f"Processando atualização de assinatura: {subscription.id}")
        
        try:
            # Buscar a assinatura no banco de dados
            db_subscription = self.subscription_repository.get_subscription_by_stripe_id(
                self.db, 
                subscription.id
            )
            
            if db_subscription:
                # Atualizar assinatura no banco de dados
                db_subscription.status = subscription.status
                db_subscription.start_date = datetime.fromtimestamp(subscription.current_period_start)
                db_subscription.end_date = datetime.fromtimestamp(subscription.current_period_end)
                db_subscription.auto_renew = not subscription.cancel_at_period_end
                
                self.subscription_repository.update_subscription(
                    self.db, 
                    db_subscription.id, 
                    db_subscription
                )
                
                logger.info(f"Assinatura {db_subscription.id} atualizada")
            else:
                logger.warning(f"Assinatura com stripe_id {subscription.id} não encontrada no banco de dados")
                
        except Exception as e:
            logger.error(f"Erro ao processar atualização de assinatura {subscription.id}: {str(e)}")
    
    async def _handle_subscription_deleted(self, subscription):
        """
        Processa um evento de customer.subscription.deleted.
        Atualiza o status da assinatura para cancelada.
        
        Args:
            subscription: Objeto da assinatura do Stripe.
        """
        logger.info(f"Processando cancelamento de assinatura: {subscription.id}")
        
        try:
            # Buscar a assinatura no banco de dados
            db_subscription = self.subscription_repository.get_subscription_by_stripe_id(
                self.db, 
                subscription.id
            )
            
            if db_subscription:
                # Atualizar assinatura no banco de dados
                db_subscription.status = "canceled"
                db_subscription.auto_renew = False
                
                self.subscription_repository.update_subscription(
                    self.db, 
                    db_subscription.id, 
                    db_subscription
                )
                
                logger.info(f"Assinatura {db_subscription.id} marcada como cancelada")
            else:
                logger.warning(f"Assinatura com stripe_id {subscription.id} não encontrada no banco de dados")
                
        except Exception as e:
            logger.error(f"Erro ao processar cancelamento de assinatura {subscription.id}: {str(e)}")
    
    def update_subscription(self, user_id: uuid.UUID, subscription_id: uuid.UUID, update_data: SubscriptionUpdateDTO):
        """
        Atualiza uma assinatura existente (renovação automática, plano, etc).
        
        Args:
            user_id: ID do usuário.
            subscription_id: ID da assinatura.
            update_data: DTO com os dados para atualização da assinatura.
            
        Returns:
            Subscription: A assinatura atualizada.
            
        Raises:
            HTTPException: Se ocorrer um erro ao atualizar a assinatura.
        """
        try:
            # Busca a assinatura no banco de dados
            subscription = self.subscription_repository.get_subscription(self.db, subscription_id)
            if not subscription:
                logger.error(f"Assinatura não encontrada: {subscription_id}")
                raise HTTPException(status_code=404, detail="Assinatura não encontrada")
            
            # Verifica se a assinatura pertence ao usuário
            if str(subscription.user_id) != str(user_id):
                logger.error(f"Usuário {user_id} não tem permissão para acessar a assinatura {subscription_id}")
                raise HTTPException(status_code=403, detail="Acesso negado a esta assinatura")
            
            # Se não tiver stripe_subscription_id, não pode atualizar no Stripe
            if not subscription.stripe_subscription_id:
                logger.error(f"Assinatura {subscription_id} não possui um ID no Stripe")
                raise HTTPException(status_code=400, detail="Assinatura não possui uma referência no Stripe")
            
            # Atualiza a assinatura no Stripe
            try:
                # Atualiza o cancel_at_period_end (o inverso de auto_renew)
                if update_data.auto_renew is not None:
                    update_subscription(
                        subscription_id=subscription.stripe_subscription_id,
                        cancel_at_period_end=not update_data.auto_renew
                    )
                    
                    # Atualiza o auto_renew no banco de dados
                    subscription.auto_renew = update_data.auto_renew
                    logger.info(f"Renovação automática da assinatura {subscription_id} atualizada para {update_data.auto_renew}")
                
                # Atualiza o plano (se fornecido)
                if update_data.plan_id:
                    # Busca o novo plano
                    new_plan = self.plan_repository.get_plan_by_id(self.db, update_data.plan_id)
                    if not new_plan or not new_plan.stripe_price_id:
                        logger.error(f"Plano {update_data.plan_id} não encontrado ou não possui um preço no Stripe")
                        raise HTTPException(status_code=404, detail="Novo plano não encontrado")
                    
                    # Obtém os detalhes da assinatura atual no Stripe
                    stripe_subscription = get_subscription(subscription.stripe_subscription_id)
                    
                    # Atualiza o plano da assinatura no Stripe
                    update_subscription(
                        subscription_id=subscription.stripe_subscription_id,
                        items=[{
                            'id': stripe_subscription.items.data[0].id,
                            'price': new_plan.stripe_price_id,
                        }]
                    )
                    
                    # Atualiza o plano no banco de dados
                    subscription.plan_id = update_data.plan_id
                    logger.info(f"Plano da assinatura {subscription_id} atualizado para {update_data.plan_id}")
                
                # Salva as alterações no banco de dados
                updated_subscription = self.subscription_repository.update_subscription(
                    self.db, 
                    subscription_id, 
                    subscription
                )
                
                return updated_subscription
                
            except Exception as e:
                logger.error(f"Erro ao atualizar assinatura no Stripe: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Erro ao atualizar assinatura no Stripe: {str(e)}")
                
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar assinatura: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar assinatura: {str(e)}")
    
    def _get_app_url(self) -> str:
        """
        Retorna a URL base da aplicação.
        
        Returns:
            str: A URL base da aplicação.
        """
        # Em produção, isso deve ser configurável através de variáveis de ambiente
        return "http://localhost:3000"
