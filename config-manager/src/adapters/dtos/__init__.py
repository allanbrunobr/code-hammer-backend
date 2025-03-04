from .message import MessageDTO as MessageDTO
from .conversation import ConversationDTO as ConversationDTO
from .content import ContentDTO as ContentDTO
from .document import DocumentDTO as DocumentDTO
from .user import UserDTO, UserCreateDTO, LoginRequest
from .token import Token
from .billing import BillingCreateDTO, BillingDTO
from .plan import PlanDTO, PlanCreateDTO
from .subscription import (
    SubscriptionCreateDTO, 
    SubscriptionDTO, 
    SubscriptionFullDTO, 
    SubscriptionResponseDTO,
    PlanDTO,
    PeriodDTO,
    PlanPeriodDTO
)
from .integration import IntegrationDTO, IntegrationCreateDTO

# Importações dos DTOs de pagamento - em um bloco try/except para não quebrar importações existentes
try:
    from .payment import (
        PaymentMethodDTO,
        CheckoutSessionCreateDTO,
        CheckoutSessionResponseDTO,
        SubscriptionUpdateDTO,
        CustomerPortalSessionDTO,
        StripeWebhookDTO,
        InvoiceDTO,
        PaymentIntentDTO,
        StripeEventDTO
    )
except ImportError:
    # Os DTOs de pagamento serão importados quando o módulo estiver disponível
    pass
