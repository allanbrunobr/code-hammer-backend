import unittest
from unittest.mock import patch, Mock
from src.services.slack import SlackService

class TestSlackService(unittest.TestCase):

    @patch('src.services.slack.requests.get')
    def test_get_channel_history(self, mock_get):
        # Mock de resposta da API do Slack
        mock_response = Mock()
        mock_response.json.return_value = {
            'messages': [
                {'ts': '1633072800.000100', 'user': 'U12345678', 'text': 'Hello world!'},
                {'ts': '1633072900.000200', 'user': 'U87654321', 'text': 'Hi there!'}
            ]
        }
        mock_get.return_value = mock_response

        # Chama o método de teste
        result = SlackService.get_channel_history()

        # Verifica se o método requests.get foi chamado com os parâmetros corretos
        mock_get.assert_called_once_with(
            'https://slack.com/api/conversations.history',
            headers={
                'Authorization': 'Bearer xoxp-7405472720739-7398955105974-7428545996432-7344022f5bf3229c95ea06c70da22f48'},
            params={'channel': 'C07CLB3S8MN'}
        )

        # Verifica o resultado
        expected_text = (
            'horário 2021-10-01 07:21:40 usuário U87654321: Hi there! \n'
            'horário 2021-10-01 07:20:00 usuário U12345678: Hello world! \n'
        )
        self.assertEqual(result, expected_text)

    @patch('src.services.slack.requests.get')
    def test_get_channel_history_exception(self, mock_get):
        # Simula uma exceção ao chamar requests.get
        mock_get.side_effect = Exception('API request failed')
        # Chama o método de teste
        result = SlackService.get_channel_history()
        # Verifica o resultado quando ocorre uma exceção
        self.assertEqual(result, '')


if __name__ == '__main__':
    unittest.main()
