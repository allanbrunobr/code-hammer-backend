import os
import json
import base64
from typing import Union, Any

from .checkers import Checkers

class Environment:

    @staticmethod
    def value_to_dict(value: Union[str, bytes]) -> dict:
        try:
            if Checkers.is_base64(value):
                decoded_bytes = base64.b64decode(value)
                value = decoded_bytes.decode('utf-8')

            dict_obj = json.loads(value)

            return dict_obj
        except Exception as e:
            raise ValueError("Erro ao converter para um dicionário JSON: {}".format(e))

    @staticmethod
    def get(name: str, default: Any = None, dict_obj: bool = False) -> Any:
        value = os.getenv(name, default)

        if dict_obj:
            try:
                return Environment.value_to_dict(value)
            except Exception:
                pass

        return value

    @staticmethod
    def get_config(name: str) -> Any:
        filename = os.getenv(name)

        if filename == None:
            return Environment.get(name=f"{name}_RAW", dict_obj=True)

        if not os.path.exists(filename):
            return None

        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except Exception as e:
            raise ValueError("Erro ao carregar o arquivo de configuração: {}".format(e))

    @staticmethod
    def path_exists(name: str) -> bool:
        filename = os.getenv(name)

        return os.path.exists(filename)
