from typing import final, List
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
        config = Environment.get_config(config)
        authorizations = Authorizations()

        if config:
            for key in config:
                description = key["description"] if "description" in key else None

                authorizations.keys.append(Authorizations.AuthorizationDetail(value=key["value"], name=key["name"], description=description))

        return authorizations

    def get_key(self, value: str) -> AuthorizationDetail|None:
        for key in self.keys:
            if key.value == value:
                return key

        return None
