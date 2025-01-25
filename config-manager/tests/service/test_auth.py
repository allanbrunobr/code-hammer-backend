# test_auth_service.py
import unittest
from unittest.mock import patch, Mock

from jose import JWTError

from src.services.auth import validate_jwt_token
from src.domain import Token
from utils import Environment


class TestAuthService(unittest.TestCase):

    @patch('src.services.auth.jwt.decode')
    def test_validate_jwt_token(self, mock_decode):
        # Mock de resposta da decodificação JWT
        mock_decode.return_value = {'sub': 'testuser'}

        token = 'mocked.jwt.token'
        result = validate_jwt_token(token)

        # Verifica se jwt.decode foi chamado com os parâmetros corretos
        mock_decode.assert_called_once_with(
            token,
            Environment.get("SECRET_KEY"),
            algorithms=[Environment.get("ALGORITHM")]
        )

        # Verifica o resultado
        expected_result = Token(username='testuser')
        self.assertEqual(result, expected_result)

    @patch('src.services.auth.jwt.decode')
    def test_validate_jwt_token_exception(self, mock_decode):
        # Simula uma exceção ao chamar jwt.decode
        mock_decode.side_effect = JWTError('Token invalid')

        token = 'mocked.jwt.token'
        result = validate_jwt_token(token)

        # Verifica o resultado quando ocorre uma exceção
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
