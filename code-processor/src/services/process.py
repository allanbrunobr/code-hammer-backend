import logging
import json

from ..adapters.dtos import UserPreferDTO
from .pubsub import PubSubClient

logger = logging.getLogger(__name__)

class ProcessService:

    def __init__(self):
        self.pub_sub_client = PubSubClient()

    def sent_message(self, message_dto: UserPreferDTO):
        """
        Envia uma mensagem para o PubSub para análise de código.
        
        Args:
            message_dto (UserPreferDTO): Dados necessários para análise
        """
        try:
            # Converte para dicionário e depois para JSON
            message_dict = message_dto.dict()
            logger.info(f"[PROCESS-SERVICE] Preparando mensagem para Pub/Sub")
            logger.info(f"[PROCESS-SERVICE] - Email: {message_dto.email}")
            logger.info(f"[PROCESS-SERVICE] - Nome: {message_dto.name}")
            logger.info(f"[PROCESS-SERVICE] - Repositório: {message_dto.repository.type}")
            logger.info(f"[PROCESS-SERVICE] - Owner: {message_dto.repository.owner}")
            logger.info(f"[PROCESS-SERVICE] - Repo: {message_dto.repository.repo}")
            logger.info(f"[PROCESS-SERVICE] - Token: {message_dto.token[:5]}...") if message_dto.token else logger.info("[PROCESS-SERVICE] - Token: Não fornecido")
            logger.info(f"[PROCESS-SERVICE] - Código vazio? {not bool(message_dto.code)}")
            logger.info(f"[PROCESS-SERVICE] - Tamanho do prompt: {len(message_dto.prompt)} caracteres")
            
            # Esconder o token no log (mas preservá-lo no objeto original)
            sanitized_dict = message_dict.copy()
            if sanitized_dict.get('token'):
                sanitized_dict['token'] = sanitized_dict['token'][:5] + '...'
            
            message_json = json.dumps(message_dict)
            
            logger.info(f"[PROCESS-SERVICE] Tamanho da mensagem JSON: {len(message_json)} bytes")
            
            # Publicar no PubSub
            message_id = self.pub_sub_client.publish_message(message_json)
            logger.info(f"[PROCESS-SERVICE] Mensagem publicada com ID: {message_id}")
            
            return message_id
            
        except Exception as e:
            logger.error(f"[PROCESS-SERVICE] Erro ao enviar mensagem para análise: {str(e)}")
            raise
