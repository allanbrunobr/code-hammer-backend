import logging
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from dotenv import load_dotenv

from ..utils.environment import Environment

load_dotenv()
logger = logging.getLogger(__name__)

class PubSubClient:

    def __init__(self):
        self.project_id = Environment.get("PROJECT_ID")
        self.topic_id = Environment.get("TOPIC_ID")
        self.subscription_id = Environment.get("SUBSCRIPTION_ID")
        
        logger.info(f"[PUBSUB] Inicializando PubSubClient - Projeto: {self.project_id}, Tópico: {self.topic_id}")
        
        # Verificar se as configurações estão presentes
        if not self.project_id or not self.topic_id:
            logger.error("[PUBSUB] PROJECT_ID e TOPIC_ID são obrigatórios para o PubSubClient")
            raise ValueError("PROJECT_ID e TOPIC_ID são obrigatórios para o PubSubClient")
        
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient() if self.subscription_id else None
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)
        self.subscription_path = (
            self.subscriber.subscription_path(self.project_id, self.subscription_id)
            if self.subscription_id else None
        )
        logger.info(f"[PUBSUB] PubSubClient inicializado - Topic path: {self.topic_path}")


    def publish_message(self, message: str, **attributes):
        """
        Publica uma mensagem no tópico Pub/Sub.
        
        Args:
            message: A mensagem a ser publicada.
            attributes: Atributos adicionais da mensagem (opcional).
            
        Returns:
            str: ID da mensagem publicada
        """
        if not message:
            logger.error("[PUBSUB] Tentativa de publicar mensagem vazia")
            raise ValueError("Mensagem não pode ser vazia")
        
        try:
            logger.info(f"[PUBSUB] Publicando mensagem - Tamanho: {len(message)} bytes")
            logger.info(f"[PUBSUB] Atributos: {attributes}")
            
            data = message.encode("utf-8")
            future = self.publisher.publish(self.topic_path, data, **attributes)
            message_id = future.result()
            logger.info(f"[PUBSUB] Mensagem publicada com ID: {message_id}")
            return message_id
        except Exception as e:
            logger.error(f"[PUBSUB] Erro ao publicar mensagem: {str(e)}")
            raise RuntimeError(f"Falha ao publicar mensagem: {str(e)}")


    def shutdown(self):
        """
        Finaliza o cliente do Pub/Sub.
        """
        try:
            if self.subscriber:
                self.subscriber.close()
            
            self.publisher.transport.close()
            logger.info("[PUBSUB] Clientes Pub/Sub finalizados com sucesso.")
        except Exception as e:
            logger.error(f"[PUBSUB] Erro ao finalizar clientes Pub/Sub: {str(e)}")
