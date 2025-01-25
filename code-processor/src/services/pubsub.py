from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from dotenv import load_dotenv

from ..utils.environment import Environment

load_dotenv()
class PubSubClient:

    def __init__(self):
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



    def shutdown(self):
        """
        Finaliza o cliente do Pub/Sub.
        """
        if self.subscriber:
            self.subscriber.close()
        self.publisher.transport.close()
        print("Clientes Pub/Sub finalizados.")
