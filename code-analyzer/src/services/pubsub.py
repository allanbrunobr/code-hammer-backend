from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from dotenv import load_dotenv

from ..utils.environment import Environment
from .request_processor import RequestProcessor
load_dotenv()
class PubSubClient:

    def __init__(self, request_processor: RequestProcessor):
        self.project_id = Environment.get("PROJECT_ID")
        self.topic_id = Environment.get("TOPIC_ID")
        self.subscription_id = Environment.get("SUBSCRIPTION_ID")
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient() if self.subscription_id else None
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)
        self.subscription_path = (
            self.subscriber.subscription_path(self.project_id, self.subscription_id)
            if self.subscription_id else None
        )
        self.request_processor = request_processor

    def publish_message(self, message: str, **attributes):
        """
        Publica uma mensagem no tópico Pub/Sub.
        :param message: A mensagem a ser publicada.
        :param attributes: Atributos adicionais da mensagem (opcional).
        """
        data = message.encode("utf-8")
        future = self.publisher.publish(self.topic_path, data, **attributes)
        print(f"Mensagem publicada: {message}")
        return future.result()

    def subscribe_messages(self, timeout=10000):
        """
        Escuta e consome mensagens da assinatura do Pub/Sub.
        :param callback: Função callback para processar as mensagens.
        :param timeout: Tempo limite para ouvir mensagens (em segundos).
        """
        if not self.subscription_id:
            raise ValueError("Assinatura (subscription_id) não foi fornecida.")

        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, callback=self.request_processor.process_message
        )
        print(f"Escutando na assinatura: {self.subscription_path}")

        try:
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()
            print(f"Ouvinte encerrado após {timeout} segundos.")

    def shutdown(self):
        """
        Finaliza o cliente do Pub/Sub.
        """
        if self.subscriber:
            self.subscriber.close()
        self.publisher.transport.close()
        print("Clientes Pub/Sub finalizados.")
