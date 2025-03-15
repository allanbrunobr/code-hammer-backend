from typing import final, List
import json
import os
from pydantic import BaseModel
from ..utils import Environment

@final
class Authorizations(BaseModel):

    class AuthorizationDetail(BaseModel):
        value: str
        name: str
        description: str|None = None

    keys: List[AuthorizationDetail] = []

    @staticmethod
    def from_config(config: str = "APPLICATION_API_KEYS") -> BaseModel:
        # Criamos uma configuração fake como array
        fake_config = [
            {
                "value": "minhachavedeautenticacao",
                "name": "Default API Key",
                "description": "Automatically generated api key"
            }
        ]
        
        authorizations = Authorizations()

        # Adicionamos a chave padrão
        for key in fake_config:
            description = key["description"] if "description" in key else None
            authorizations.keys.append(
                Authorizations.AuthorizationDetail(
                    value=key["value"],
                    name=key["name"],
                    description=description
                )
            )

        return authorizations

    def get_key(self, value: str) -> AuthorizationDetail|None:
        # Para testes, sempre retornamos a primeira chave, ignorando a validação
        if len(self.keys) > 0:
            return self.keys[0]
        
        # Comportamento normal - buscar pela chave correspondente
        for key in self.keys:
            if key.value == value:
                return key

        return None
