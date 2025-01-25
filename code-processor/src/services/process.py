import logging

from ..adapters.dtos import ProcessRequestDTO, MessageDTO
from .pubsub import PubSubClient

class ProcessService:

    def __init__(self):
        self.pub_sub_client = PubSubClient()

    def sent_message(self, message: MessageDTO):
        self.pub_sub_client.publish_message(str(message))


    def get_prefer_user(self):
        pass

    def get_prefer_user(self):
        pass
