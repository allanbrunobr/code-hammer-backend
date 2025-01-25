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

### logando no GCP

gcloud init 
gcloud auth login
gcloud config set project  br-sef-mg-cld-01
gcloud auth application-default login
gcloud auth application-default set-quota-project  br-sef-mg-cld-01

### Descrição dos Diretórios:

- `adapters`: Contém implementações que convertem dados entre diferentes camadas ou interfaces do sistema.
  - `dtos`: Data Transfer Objects, usados para transportar dados entre processos, especialmente entre o domínio e as interfaces externas.
- `domain`: Abriga as regras de negócio e a lógica central do sistema. Esta camada é independente de frameworks e tecnologias específicas.
- `entities`: Contém as entidades do domínio, que são os objetos principais do negócio com suas propriedades e comportamentos.
- `routers`: Define as rotas de navegação e endpoints da aplicação, separado para melhor modularização e clareza.
- `services`: Inclui a lógica de aplicação que coordena a execução de tarefas, orquestra diferentes entidades e aplica regras de negócio mais complexas.
