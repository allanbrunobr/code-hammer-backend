# CodeHammer - Analisador de Código com IA

Plataforma de análise de código que utiliza IA para identificar problemas, bugs, vulnerabilidades e fornecer recomendações para melhorar a qualidade do código.

## Visão Geral da Arquitetura

O sistema é composto por três serviços principais:

1. **config-manager**: Responsável pelo gerenciamento de usuários, integrações e configurações.
2. **code-processor**: Recebe solicitações de análise de código e as envia para processamento.
3. **code-analyzer**: Utiliza IA para analisar o código e postar comentários nos repositórios.

### Fluxo de Análise de Código

1. O usuário solicita uma análise de código através da API ou do frontend.
2. O `code-processor` busca as credenciais do usuário e envia uma mensagem para o Pub/Sub.
3. O `code-analyzer` processa a mensagem, analisa o código com a IA e posta um comentário no repositório.

## Pré-requisitos

- Docker e Docker Compose
- Conta no Google Cloud com Vertex AI e Pub/Sub configurados
- Credenciais de serviço do Google Cloud com permissões para Vertex AI e Pub/Sub

## Configuração

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/codehammer.git
   cd codehammer
   ```

2. Copie o arquivo `.env.example` para `.env` e preencha as variáveis:
   ```
   cp .env.example .env
   ```

3. Configure as credenciais do Google Cloud:
   - Faça o download das credenciais de serviço do Google Cloud
   - Atualize o caminho em `GOOGLE_APPLICATION_CREDENTIALS_PATH` no arquivo `.env`

4. Inicie os serviços:
   ```
   docker-compose up -d
   ```

## Uso

### API de Análise de Código

#### Endpoint para Análise de Código

```
POST /api/v1/analysis
```

**Corpo da Requisição:**
```json
{
  "email": "user@example.com",
  "code": "def example():\n    print('Hello World!')",
  "language": "python",
  "file_name": "example.py",
  "analysis_types": ["codeQuality", "security"],
  "integration_id": "550e8400-e29b-41d4-a716-446655440000",
  "post_comment": true
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Code analysis request submitted successfully",
  "timestamp": "2025-03-02T12:34:56.789Z",
  "data": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Code analysis request received. Results will be processed in the background.",
    "status": "processing"
  },
  "errors": null
}
```

### Configuração de Integrações

Para que o sistema possa acessar e comentar em repositórios, é necessário configurar integrações com provedores de repositório (GitHub, GitLab, Azure DevOps ou Bitbucket).

#### Criar uma Nova Integração

```
POST /api/v1/integrations
```

**Corpo da Requisição:**
```json
{
  "name": "Meu Repositório GitHub",
  "repository": "github",
  "repository_token": "ghp_your_github_token",
  "repository_url": "github.com/username/repo",
  "user_id": "f70cf81c-3d1d-4cf0-8598-91be25d49b1e",
  "analyze_types": "vulnerabilidadesOwasp,componentizacao,otimizacaoBigO,duplicacao"
}
```

## Desenvolvimento

### Estrutura do Código

```
codehammer/
├── config-manager/     # Gerenciamento de usuários e configurações
├── code-processor/     # Processamento de solicitações
├── code-analyzer/      # Análise de código com IA
├── docker-compose.yml  # Configuração Docker
└── .env                # Variáveis de ambiente
```

### Modelos de Dados

#### Integrations
- `id`: UUID - Identificador único
- `name`: String - Nome da integração
- `repository`: String - Tipo de repositório (github, gitlab, etc.)
- `repository_token`: String - Token de autenticação
- `repository_url`: String - URL do repositório
- `user_id`: UUID - ID do usuário proprietário
- `analyze_types`: String - Tipos de análise a realizar

#### Subscriptions
- `id`: UUID - Identificador único
- `status`: String - Status da assinatura
- `plan_id`: UUID - ID do plano
- `user_id`: UUID - ID do usuário
- `start_date`: DateTime - Data de início
- `end_date`: DateTime - Data de término
- `remaining_file_quota`: Integer - Cota de arquivos restante
- `auto_renew`: Boolean - Renovação automática

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
