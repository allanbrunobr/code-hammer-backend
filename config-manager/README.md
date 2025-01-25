# ChatAgent

Este serviço é responsável por disponibilizar uma API Rest.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi)
![PyPI - Version](https://img.shields.io/pypi/v/fastapi?label=FastApi)
![PyPI - Version](https://img.shields.io/pypi/v/SQLAlchemy?label=SQLAlchemy)
![PyPI - Version](https://img.shields.io/pypi/v/uvicorn?label=Uvicorn)

## Stack utilizada

**Back-end:** Python, FastAPI, SQLAlchemy e Uvicorn

## Configurando a aplicação

> Para que a aplicação possa executar, será necessário configurar as api-keys. Estas configurações podem ser feitas de duas formas, sendo elas JSON ou RAW via variável de ambiente com os dados codificado em Base64. Para a configuração em JSON e necessário a criação do arquivo `api-keys.json` na raiz do projeto.

### Variáveis de ambientes para o formato RAW

> Atribua o valor para as variáveis de ambientes com os JSON codificado em Base64.

- APPLICATION_API_KEYS_RAW: API Keys para acesso à API

### Variáveis de ambientes para o Formato JSON

> Atribua o endereço do arquivo JSON para as varáveis de ambientes.

- APPLICATION_API_KEYS: Arquivo onde se encontra as API Keys

### Arquivo de configuração API Keys

> Para adicionar uma nova API Key, deverá adicionar mais um item informando o valor da key e o nome, abaixo e demonstrado um exemplo

```json
[
  {"value": "s2405141900-3af66526e0a344fee6f1a1ac3fa2", "name": "Sample"}
]
```

## Inicializando o projeto

Caso esteja iniciando um projeto, o comando abaixo inicializa uma estrutura padrão para que possa da continuidade. Caso deseja inicializar uma estrutura padrão execute o comando fornecido abaixo.

> Para o comando abaixo, será executado informando o nome `sample`, título `Sample` e o caminho `/v1` 

```sh
python.exe ./utils/initialize.py --name="sample" --title="Sample" --path="/v1"

```

> Para ver todas as opções disponíveis execute

```sh
python.exe ./utils/initialize.py --help

```

***Obs.: O caminha informado irá ser concatenado como `/api`, informando `/v1` ficará `/api/v1`. A pasta o qual irá ficar o código-fonte do projeto nesse caso será `sample`.*** 

## Rodando localmente

Os modelos de execução demostrado abaixo, roda a aplicação na porta 5000, o qual pode ser acessada pela URL http://localhost:5000.
Para verificar a vivacidade da execução acesse a URL http://localhost:5000/api/v1/actuator/health/liveness. Caso queira acessar a documentação acesse a URL http://localhost:5000/docs.

### Executando pelo python no local

Para executar no shell em modo de desenvolvedor, execute o comando abaixo

```sh
python.exe local.py

```

***Obs.: A aplicação irá ser rodada na porta 5000 com o reload e logs de debug habilitados***

### Executando pelo docker no local

Iremos realizar o build, supondo que o projeto seja `api-sample`, após o build completar deverá ser iniciado o servidor expondo a porta 5000, execute os comandos abaixo.

> Realizando o build

```sh
docker build -t api-sample .

```

> Executando o docker

```sh
docker run -d -p 5000:80 api-sample

```

## Adicionando rota

> Iremos adicionar a rota `/items` o qual irá retornar uma lista de itens, o exemplo irá usar como nome do projeto `src`, para isso entre na pasta de código-fonte do projeto, e siga os passos a seguir.

### Código-fonte

Supondo que a pasta do código-fonte (o nome da pasta será o mesmo do nome do projeto) ficou como `src`, entre na pasta para realizar os próximos passos.

### Criando DTO

Para começarmos, iremos criar o Data Transfer Object (DTO) dentro da pasta `adapters/dtos` com o nome de arquivo `item.py`. Jogue o conteúdo abaixo no arquivo.

```py
from pydantic import BaseModel

class ItemDTO(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

```

Exporte o DTO no arquivo `adapters/dtos/__init__.py` para que possa ser acessado, conforme demostrado abaixo.

```py
# other lines...
from .item import ItemDTO as ItemDTO

```

### Criando Serviço

Crie um serviço na pasta `services` com o nome de arquivo `item.py`.

```py
from ..adapters.dtos import ItemDTO

class ItemService:
    def all(self) -> ItemDTO:
        item = {
            "name": "Sample item",
            "description": "This is just a demo item",
            "price": 99.99,
            "tax": 10.0
        }
        return ItemDTO(**item)

```

Exporte o serviço no arquivo `services/__init__.py` para que possa ser acessado, conforme demostrado abaixo.

```py
# other lines...
from .item import ItemService as ItemService

```

### Criando Rota

Agora precisamos criar a rota para ser acessada, crie a rota na pasta `routers` com o nome de arquivo `item.py`.

```py
from fastapi import APIRouter
from ..adapters.dtos import ItemDTO
from ..services import ItemService

router = APIRouter(
    prefix="/items",
    tags=["items"]
)
item = ItemService()

@router.get("/")
def root() -> ItemDTO:
    return item.all()

```

Pronto, agora que temos o DTO, serviço e rota criado só precisamos incluir a nova rota no APP. Para isso, dentro do arquivo `main.py`, realiza a inclusão conforme demostrado abaixo.

```py
# other lines...
from .routers import item
# other lines...
api_router.include_router(item.router)
# other lines...

```

### Resultado da nova Rota

Tudo realizado e só rodar a aplicação e acessar a rota `/items` que irá apresentar um resultado conforme demostrado abaixo.

```json
[
  {
    "name": "Sample item",
    "description": "This is just a demo item",
    "price": 99.99,
    "tax": 10
  }
]

```

## Referência

- [Python Docs](https://www.python.org/doc/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [API Gemini](https://ai.google.dev/gemini-api/docs/get-started/tutorial?hl=pt-br&lang=python)

# Links uteis

- [Python Package](https://pypi.org)
