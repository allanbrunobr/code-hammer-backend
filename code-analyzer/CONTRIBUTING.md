# Diretrizes de contribuição

## Isolando Projeto

Configurar o ambiente para execução do projeto.

### Pyenv

### Configurando versão

Iremos realizar a configuração da versão Python 3.8.6.

> Caso não tenha a versão instalada, execute o comando abaixo informando a versão

```shell
pyenv install 3.8.6

```

> Configurando versão

```shell
pyenv shell 3.8.6

```

> Criando ambiente virtual

```shell
python -m venv project

```

> Ativando ambiente virtual

```shell
source project/bin/activate

```
> Logando no GCP

```shell

```

> Contrato de dados do Pub/Sub
````json
gcloud pubsub topics publish code-to-analyze --message='{
  "name": "bruno",
  "email": "allanbruno@gmail.com",
  "code": "print(\"hello world from feature branch\")",
  "token": "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",
  "language": "python",
  "prompt": "analyze code",
  "repository": {
    "type": "Github",
    "owner": "allanbrunobr",
    "repo": "code-analysis-test",
    "pull_request_number": "1",
    "project_id": "code-analysis-test",
    "repo_slug": "code-analysis-test",
    "pull_request_id": "1",
    "workspace": "code-analysis-test"
  }
}'

````
````shell
gcloud pubsub topics publish code-to-analyze --message="{\"name\": \"bruno\", \"email\": \"allanbruno@gmail.com\", \"code\": \"print('hello word')\", \"token\": \"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\", \"language\": \"python\", \"prompt\": \"analise algum erro de sintaxe\", \"repository\": {\"type\": \"Github\", \"owner\": \"allanbrunobr\", \"repo\": \"json-formatter\", \"pull_request_number\": \"1\", \"project_id\": \"json-formatter\", \"repo_slug\": \"json-formatter\", \"pull_request_id\": \"1\", \"workspace\": \"json-formatter\"}}"
````

## Instalando pacotes

Caso estejá usando o Windows e apresente um erro similar a `ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory:`, ative os Caminhos Longos no Windows isso pode resolver o problema.

### Ativar Caminhos Longos no Windows

O Windows 10 (versão 1607 e posteriores) permite habilitar caminhos longos. Você pode habilitar isso através do Editor de Política de Grupo.

- Pressione Win + R, digite gpedit.msc e pressione Enter.
- Navegue até Configuração do Computador > Modelos Administrativos > Sistema > Sistema de Arquivos.
- Habilite a configuração Ativar Caminhos Win32 Longos.

## Estutura de diretórios

A estrutura de diretórios abaixo segue a Clean Architecture e os princípios do SOLID.

```txt
src
 |-- adapters
 |   \-- dtos
 |-- domain
 |-- entities
 |-- routers
 \-- services

```

### Descrição dos Diretórios:

- `adapters`: Contém implementações que convertem dados entre diferentes camadas ou interfaces do sistema.
  - `dtos`: Data Transfer Objects, usados para transportar dados entre processos, especialmente entre o domínio e as interfaces externas.
- `domain`: Abriga as regras de negócio e a lógica central do sistema. Esta camada é independente de frameworks e tecnologias específicas.
- `entities`: Contém as entidades do domínio, que são os objetos principais do negócio com suas propriedades e comportamentos.
- `routers`: Define as rotas de navegação e endpoints da aplicação, separado para melhor modularização e clareza.
- `services`: Inclui a lógica de aplicação que coordena a execução de tarefas, orquestra diferentes entidades e aplica regras de negócio mais complexas.
