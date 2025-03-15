import requests

from .comment_poster import CommentPoster
from ...adapters.dtos import UserPreferDTO

class BitbucketCommentPoster(CommentPoster):
    def post_comment(self, user_prefer: UserPreferDTO, comment: str):
        url = f'https://api.bitbucket.org/2.0/repositories/{user_prefer.repository.workspace}/{user_prefer.repository.repo_slug}/pullrequests/{user_prefer.repository.pull_request_id}/comments'
        headers = {
            'Authorization': f'Bearer {user_prefer.repository.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'content': {
                'raw': comment
            }
        }

        response = self.request_client.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f'Erro: {response.status_code} - {response.text}')