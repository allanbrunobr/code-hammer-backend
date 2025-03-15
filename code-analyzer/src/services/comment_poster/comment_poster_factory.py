import logging

from .azure import AzureDevOpsCommentPoster
from .bitbucket import BitbucketCommentPoster
from .comment_poster import CommentPoster
from .github import GitHubCommentPoster
from .gitlab import GitLabCommentPoster
from ...adapters.dtos import UserPreferDTO, TypeRepositoryEnum

logger = logging.getLogger(__name__)

class CommentPosterFactory:
    """
    Factory para criar instâncias de CommentPoster de acordo com o tipo de repositório.
    """

    @staticmethod
    def create_comment_poster(user_prefer: UserPreferDTO) -> CommentPoster:
        """
        Cria uma instância de CommentPoster baseada no tipo de repositório.

        Args:
            user_prefer: UserPreferDTO contendo o tipo de repositório, 
                         autenticação e detalhes de configuração

        Returns:
            CommentPoster: Uma instância do comentador apropriado
            
        Raises:
            ValueError: Se o tipo de repositório for inválido
        """
        logger.info(f"Creating comment poster for repository type: {user_prefer.repository.type}")
        
        if user_prefer.repository.type == TypeRepositoryEnum.GITLAB:
            return GitLabCommentPoster()
        elif user_prefer.repository.type == TypeRepositoryEnum.GITHUB:
            return GitHubCommentPoster()
        elif user_prefer.repository.type == TypeRepositoryEnum.BITBUCKET:
            return BitbucketCommentPoster()
        elif user_prefer.repository.type == TypeRepositoryEnum.AZURE:
            return AzureDevOpsCommentPoster()
        else:
            error_msg = f'Invalid repository type: {user_prefer.repository.type}'
            logger.error(error_msg)
            raise ValueError(error_msg)
