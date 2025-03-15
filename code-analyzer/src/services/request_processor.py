from abc import ABC, abstractmethod
from ..adapters.dtos import UserPreferDTO


class RequestProcessor(ABC):

    @staticmethod
    @abstractmethod
    def process_message(message):
        pass







