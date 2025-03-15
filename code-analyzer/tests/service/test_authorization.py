import os
from dotenv import load_dotenv
load_dotenv()
import unittest
from unittest.mock import MagicMock, patch
import base64
from fastapi import HTTPException
from src.services.authorization import AuthorizationService

class TestAuthorizationService(unittest.TestCase):

    @patch('src.entities.Authorizations.from_config')
    def setUp(self, mock_from_config):
        # Configura os mocks
        self.mock_authorizations = MagicMock()
        mock_from_config.return_value = self.mock_authorizations
        self.service = AuthorizationService()

        # Configura a instância de processors do serviço para usar o mock
        self.service.processors = self.mock_authorizations

    def test_valid_authorization(self):
        valid_token = "s2405141900-3af66526e0a344fee6f1a1ac3fa2"
        # Configura o comportamento esperado para a chave de API válida
        self.mock_authorizations.get_key.return_value = valid_token

        # Cria um cabeçalho de autorização válido
        authorization = "Basic " + base64.b64encode(valid_token.encode('utf-8')).decode('utf-8')

        # Adiciona um print para depuração
        print("Testing valid authorization with:", authorization)

        # Chama o método de validação
        try:
            result = self.service.validate(authorization)
            # Verifica se o método get_key foi chamado
            self.assertTrue(self.mock_authorizations.get_key.called)
            # Verifica o argumento passado para get_key
            self.assertEqual(self.mock_authorizations.get_key.call_args[0][0], valid_token)
            # Verifica o resultado
            self.assertTrue(result)
        except HTTPException as e:
            # Se uma exceção for lançada, imprima o detalhe
            print(f"HTTPException raised: {e.detail}")
            raise

    def test_invalid_authorization_header(self):
        with self.assertRaises(HTTPException) as context:
            self.service.validate("Invalid header")

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Não foi possível validar as credenciais")
        self.assertEqual(context.exception.headers, {"WWW-Authenticate": "Basic"})

    def test_decode_error(self):
        with self.assertRaises(HTTPException) as context:
            self.service.validate("Basic InvalidBase64")

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Não foi possível validar as credenciais")
        self.assertEqual(context.exception.headers, {"WWW-Authenticate": "Basic"})

    def test_unauthorized_key(self):
        # Configura o comportamento esperado para a chave de API inválida
        self.mock_authorizations.get_key.return_value = False

        authorization = "Basic " + base64.b64encode(b"invalid_api_key").decode('utf-8')

        with self.assertRaises(HTTPException) as context:
            self.service.validate(authorization)

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, [
            {"msg": "Desculpe, você não tem permissão para acessar este recurso"},
            {
                "msg": "Por favor, verifique suas credenciais ou entre em contato com o administrador do sistema para obter acesso autorizado"}
        ])


if __name__ == '__main__':
    unittest.main()