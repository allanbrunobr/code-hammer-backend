import requests

from .comment_poster import CommentPoster
from ...adapters.dtos import UserPreferDTO


class GitLabCommentPoster(CommentPoster):


    def post_comment(self, user_prefer: UserPreferDTO, comment: str):

        url = f'https://gitlab.com/api/v4/projects/{user_prefer.repository.project_id}/merge_requests/{user_prefer.repository.pull_request_id}/notes'
        print(url)
        headers = {
            'PRIVATE-TOKEN': user_prefer.repository.token,
            'Content-Type': 'application/json'
        }
        data = {
            'body': comment
        }
        print(url, headers, data)
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return response.json()
        else:

            raise Exception(f'Erro: {response.status_code} - {response.text}')

