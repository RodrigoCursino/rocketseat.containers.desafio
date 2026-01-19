# 📋 Documentação do Docker Compose

Esta documentação explica detalhadamente cada seção e item do arquivo `docker-compose.yaml`, focando no ambiente **Vault + MySQL + FastAPI** com gerenciamento dinâmico de credenciais. O setup utiliza o **HashiCorp Vault** para segurança, eliminando senhas fixas no código.

---

## 🏗️ Estrutura Geral

O `docker-compose.yaml` define serviços, volumes e redes para orquestrar um ambiente seguro. Ele inclui:
- **Serviços**: Containers para Vault, banco de dados, agentes e aplicações.
- **Volumes**: Persistência de dados.
- **Redes**: Isolamento de comunicação.

Todos os serviços estão conectados à rede `desafio-rocketseat-containers` para comunicação interna.

---

## 🐳 Serviços

### 1. `vault`
- **Imagem**: `hashicorp/vault:1.21.0`
- **Container Name**: `vault`
- **Restart**: `always` (reinicia automaticamente em caso de falha).
- **Environment**:
  - `VAULT_ADDR: http://vault:8200`: Endereço interno do Vault.
  - `VAULT_DISABLE_MLOCK: "true"`: Desabilita o bloqueio de memória (útil em containers sem privilégios).
- **Ports**: `8200:8200` (expõe a porta 8200 do host para acessar a UI/API do Vault).
- **Volumes**:
  - `./vault/data:/vault/data`: Persiste dados do Vault (chaves, selos).
  - `./vault/config:/vault/config`: Configuração do Vault (arquivo `vault.hcl`).
  - `./vault/policies:/vault/policies`: Políticas de acesso (ex.: `fastapi-policy.hcl`).
  - `./vault/logs:/var/log/vault`: Logs do Vault.
- **Command**: `vault server -config=/vault/config/vault.hcl` (inicia o servidor Vault com configuração personalizada).
- **Cap_Add**: `IPC_LOCK` (permite bloqueio de memória para segurança).
- **Networks**: `desafio-rocketseat-containers`.
- **Propósito**: Servidor central do Vault para gerenciamento de secrets. Deve ser inicializado e "unsealed" manualmente (veja [configuracao_vault.md](configuracao_vault.md)).

### 2. `mysql`
- **Imagem**: `mysql:8.0`
- **Container Name**: `mysql`
- **Restart**: `always`.
- **Environment**:
  - `MYSQL_ROOT_PASSWORD: root`: Senha do usuário root (usada apenas para setup inicial; credenciais dinâmicas são gerenciadas pelo Vault).
  - `MYSQL_DATABASE: appdb`: Banco padrão criado.
- **Ports**: `3306:3306` (expõe a porta para acesso externo, se necessário).
- **Volumes**: `mysql-data:/var/lib/mysql` (persiste dados do banco).
- **Networks**: `desafio-rocketseat-containers`.
- **Propósito**: Banco de dados MySQL. O Vault cria usuários dinâmicos para acesso seguro, evitando senhas fixas.

### 3. `vault-agent-alembic`
- **Imagem**: `hashicorp/vault:1.21.0`
- **Container Name**: `vault-agent-alembic`
- **User**: `100:100` (usuário não-root para segurança).
- **Depends_On**: `vault` (aguarda o Vault iniciar).
- **Environment**: `SKIP_SETCAP=true` (evita configurações de kernel desnecessárias).
- **Command**: `vault agent -config=/vault/agent-alembic.hcl` (executa o Vault Agent com configuração específica para Alembic).
- **Volumes**:
  - `./vault/agent-alembic.hcl:/vault/agent-alembic.hcl:ro`: Configuração do agente (somente leitura).
  - `./vault/agent-alembic/auth:/vault/auth:rw`: Tokens de autenticação.
  - `./vault/templates:/vault/templates:ro`: Templates para gerar secrets.
  - `./vault/agent-alembic/secrets:/vault/secrets`: Diretório onde secrets são escritos (ex.: `database.env`).
- **Networks**: `desafio-rocketseat-containers`.
- **Propósito**: Vault Agent dedicado ao Alembic. Autentica via AppRole e gera credenciais dinâmicas para migrações de banco.

### 4. `alembic`
- **Build**: `./app` (usa o Dockerfile da aplicação).
- **Container Name**: `alembic`
- **Command**: `sh -c "while [ ! -f /vault/secrets/database.env ]; do sleep 1; done; alembic revision --autogenerate -m 'create tables'; alembic upgrade head"` (aguarda secrets, gera migrações automaticamente e aplica).
- **Volumes**: `./vault/agent-alembic/secrets:/vault/secrets` (acessa secrets gerados pelo agente).
- **Depends_On**: `vault-agent-alembic` (aguarda o agente).
- **Networks**: `desafio-rocketseat-containers`.
- **Propósito**: Executa migrações do banco usando Alembic. Garante que tabelas (ex.: `products`) sejam criadas antes da aplicação iniciar.

### 5. `vault-agent-fastapi`
- **Imagem**: `hashicorp/vault:1.21.0`
- **Container Name**: `vault-agent-fastapi`
- **User**: `100:100`.
- **Depends_On**: `vault`.
- **Environment**: `SKIP_SETCAP=true`.
- **Command**: `vault agent -config=/vault/agent-fastapi.hcl`.
- **Volumes**:
  - `./vault/agent-fastapi.hcl:/vault/agent-fastapi.hcl:ro`.
  - `./vault/agent-fastapi/auth:/vault/auth:rw`.
  - `./vault/templates:/vault/templates:ro`.
  - `./vault/agent-fastapi/secrets:/vault/secrets`.
- **Networks**: `desafio-rocketseat-containers`.
- **Propósito**: Vault Agent dedicado ao FastAPI. Fornece credenciais dinâmicas para a aplicação sem acesso direto ao Vault.

### 6. `fastapi`
- **Build**: `./app`.
- **Container Name**: `fastapi`
- **Restart**: `always`.
- **Command**:
  ```
  sh -c "
  while [ ! -f /vault/secrets/database.env ]; do
    echo '⏳ aguardando secrets do Vault...'
    sleep 1
  done
  . /vault/secrets/database.env
  exec uvicorn src.app:api --host 0.0.0.0 --port 3000
  "
  ``` (aguarda secrets, carrega variáveis de ambiente e inicia o servidor Uvicorn).
- **Ports**: `3000:3000` (expõe a API).
- **Volumes**: `./vault/agent-fastapi/secrets:/vault/secrets`.
- **Depends_On**: `vault-agent-fastapi`, `mysql`, `alembic` (garante ordem de inicialização).
- **Networks**: `desafio-rocketseat-containers`.
- **Propósito**: Aplicação FastAPI. Consome secrets locais para conectar ao banco de forma segura.

---

## 💾 Volumes

- `mysql-data`: Volume nomeado para persistir dados do MySQL (evita perda em reinicializações).
- `vault-secrets-fastapi`: Declarado mas não usado (pode ser removido ou ajustado).
- `vault-secrets-alembic`: Declarado mas não usado (pode ser removido ou ajustado).

**Nota**: Os agentes usam bind mounts (`./vault/...`) para acessar arquivos locais, garantindo controle sobre secrets.

---

## 🌐 Networks

- `desafio-rocketseat-containers`:
  - **Name**: `desafio-rocketseat-containers`.
  - **Driver**: `bridge` (rede isolada para comunicação entre containers).
  - **Propósito**: Permite comunicação interna (ex.: FastAPI acessa MySQL via `mysql:3306`), sem exposição externa desnecessária.

---

## 🔧 Boas Práticas e Observações

- **Segurança**: Nenhum serviço expõe credenciais diretamente. O Vault gerencia tudo dinamicamente.
- **Ordem de Inicialização**: `depends_on` garante que dependências (ex.: Vault antes dos agentes) sejam atendidas.
- **Persistência**: Volumes evitam perda de dados em restarts.
- **Debugging**: Use `docker-compose logs <service>` para verificar logs.
- **Execução**: Para subir tudo: `docker-compose up --build`. Para serviços específicos: `docker-compose up vault mysql -d`.

Essa configuração segue princípios DevOps como isolamento, least privilege e automação. Para mais detalhes, consulte o [README.md](README.md) ou [configuracao_vault.md](configuracao_vault.md).