from abc import ABC, abstractmethod
import requests
import logging
from typing import Dict, Any
from ...adapters.dtos import UserPreferDTO

class CommentPoster(ABC):
    """
    Classe base abstrata para posters de comentários em diferentes plataformas.
    """
    def __init__(self):
        self.request_client = requests
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def post_comment(self, user_prefer: UserPreferDTO, comment: str) -> Dict[str, Any]:
        """
        Posta um comentário em um repositório.
        
        Args:
            user_prefer: Preferências e dados do usuário
            comment: Comentário a ser postado
            
        Returns:
            Dict[str, Any]: Resposta da API do repositório
        """
        pass
