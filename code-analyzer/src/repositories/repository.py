from typing import Callable
from abc import ABC, abstractmethod

class BaseRepository(ABC):

    @abstractmethod
    def execute_query(self, query: str, params: dict = None, entity: Callable = dict):
        pass
