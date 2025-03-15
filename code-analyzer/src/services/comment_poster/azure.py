import requests
from .comment_poster import CommentPoster
from ...adapters.dtos import UserPreferDTO


class AzureDevOpsCommentPoster(CommentPoster):

    def post_comment(self, user_prefer: UserPreferDTO, comment: str):
        url = f'https://dev.azure.com/{user_prefer.repository.organization}/{user_prefer.repository.project}/_apis/git/repositories/{user_prefer.repository.repo}/pullRequests/{user_prefer.repository.pull_request_id}/threads?api-version=6.0'
        headers = {
            'Authorization': f'Basic {user_prefer.repository.token}',
            'Content-Type': 'application/json'
        }
        data = {
            "comments": [
                {
                    "parentCommentId": 0,
                    "content": comment,
                    "commentType": 1
                }
            ]
        }

        response = self.request_client.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Erro: {response.status_code} - {response.text}')
