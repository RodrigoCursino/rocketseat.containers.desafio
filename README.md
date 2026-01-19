# 🚀 Desafio Rocketseat – Containers

Documentação **completa, revisada e organizada** para configuração de um ambiente **Vault + MySQL + FastAPI** utilizando **Docker Compose**, com foco em **gerenciamento dinâmico de credenciais**, **segurança** e **boas práticas DevOps**.

---

## 📌 Visão Geral

Este projeto demonstra como eliminar o uso de **senhas fixas** em aplicações backend, utilizando o **HashiCorp Vault** para **criar, gerenciar, rotacionar e revogar credenciais de banco de dados automaticamente**.

A aplicação **FastAPI** e o **Alembic** **não acessam o Vault diretamente**. Toda a comunicação é realizada por meio do **Vault Agent**, utilizando **AppRole**, garantindo isolamento, segurança e aderência ao princípio de *least privilege*.

---

## 🎯 Objetivos do Desafio

* Subir um ambiente completo com Docker Compose
* Executar o Vault fora do modo *dev*
* Criar usuários dinâmicos no MySQL
* Rotacionar credenciais automaticamente
* Integrar FastAPI e Alembic de forma segura ao Vault
* Eliminar segredos hardcoded no código

---

## 🧩 Stack Utilizada

* Docker / Docker Compose
* HashiCorp Vault 1.21
* MySQL 8.0
* FastAPI
* Alembic
* Python 3.12
* Poetry

---

## 📁 Estrutura Geral do Projeto

```bash
.
├── docker-compose.yaml
├── build.sh
├── vault/
│   ├── config/
│   │   └── vault.hcl
│   ├── policies/
│   │   ├── fastapi-policy.hcl
│   │   └── alembic-policy.hcl
│   ├── templates/
│   │   ├── fastapi.ctmpl
│   │   └── alembic.ctmpl
│   ├── agent-fastapi/
│   │   ├── auth/
│   │   └── secrets/
│   └── agent-alembic/
│       ├── auth/
│       └── secrets/
├── app/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── poetry.lock
│   ├── alembic.ini
│   ├── alembic/
│   └── src/
```

---

## 1️⃣ Orquestração com Docker Compose

O arquivo `docker-compose.yaml` é responsável por subir:

* Vault (servidor)
* MySQL
* Vault Agent (FastAPI)
* Vault Agent (Alembic)
* Aplicação FastAPI
* Serviço Alembic

📌 **Importante:**

* O MySQL não é exposto externamente
* Apenas o Vault possui credenciais administrativas do banco
* As aplicações consomem apenas arquivos de secrets locais

> O conteúdo completo do `docker-compose.yaml` permanece conforme definido no projeto.

---

## 2️⃣ Subindo o Ambiente

```bash
docker compose up --build -d
```

Esse comando sobe os serviços base (Vault e MySQL).

---

## 3️⃣ Inicialização e Unseal do Vault

### Acessar o container do Vault

```bash
docker exec -it vault sh
```

### Inicializar o Vault

```bash
vault operator init
```

Esse comando gera:

* 🔐 5 **Unseal Keys**
* 🗝️ 1 **Root Token**

> ⚠️ Guarde essas informações com segurança

### Quebrar o selo (Unseal)

Execute o comando **3 vezes**, usando chaves diferentes:

```bash
vault operator unseal <UNSEAL_KEY>
```

### Login administrativo

```bash
vault login <ROOT_TOKEN>
```

---

## 4️⃣ Configuração do Vault (Database Engine)

### Ativar o secrets engine de database

```bash
vault secrets enable database
```

Verificar:

```bash
vault secrets list
```

---

## 5️⃣ Configurando o Acesso Vault → MySQL

```bash
vault write database/config/mysql \
  plugin_name=mysql-database-plugin \
  connection_url="{{username}}:{{password}}@tcp(mysql:3306)/" \
  allowed_roles="alembic-role,fastapi-role" \
  username="root" \
  password="root"
```

📌 Observações importantes:

* `mysql` é o nome do serviço no Docker Compose
* O usuário `root` é utilizado **apenas internamente pelo Vault**
* Nenhuma aplicação recebe acesso administrativo

---

## 6️⃣ Criação das Roles de Banco de Dados

### FastAPI – Permissões CRUD

```bash
vault write database/roles/fastapi-role \
  db_name=mysql \
  creation_statements="
    CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';
    GRANT SELECT, INSERT, UPDATE, DELETE ON appdb.* TO '{{name}}'@'%';
  " \
  default_ttl="1h" \
  max_ttl="24h"
```

### Alembic – Permissões Administrativas

```bash
vault write database/roles/alembic-role \
  db_name=mysql \
  creation_statements="
    CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';
    GRANT ALL PRIVILEGES ON appdb.* TO '{{name}}'@'%';
  " \
  default_ttl="15m" \
  max_ttl="1h"
```

---

## 7️⃣ Policies

As **policies** definem quais paths do Vault cada aplicação pode acessar.

### FastAPI

```hcl
path "database/creds/fastapi-role" {
  capabilities = ["read"]
}
```

### Alembic

```hcl
path "database/creds/alembic-role" {
  capabilities = ["read"]
}
```

Aplicar:

```bash
vault policy write fastapi-policy /vault/policies/fastapi-policy.hcl
vault policy write alembic-policy /vault/policies/alembic-policy.hcl
```

---

## 8️⃣ AppRole e Vault Agent

### O que é AppRole?

AppRole é um método de autenticação do Vault voltado para **aplicações e serviços**, composto por:

* `role_id` → identidade da aplicação
* `secret_id` → segredo sensível (semelhante a uma senha)

Esses dados são consumidos **exclusivamente pelo Vault Agent**, não pela aplicação.

### Habilitar AppRole

```bash
vault auth enable approle
```

### Criar AppRoles

```bash
vault write auth/approle/role/fastapi \
  token_policies="fastapi-policy" \
  token_ttl=1h \
  token_max_ttl=4h

vault write auth/approle/role/alembic \
  token_policies="alembic-policy" \
  token_ttl=1h \
  token_max_ttl=4h
```

### Gerar credenciais

```bash
vault read auth/approle/role/fastapi/role-id
vault write -f auth/approle/role/fastapi/secret-id

vault read auth/approle/role/alembic/role-id
vault write -f auth/approle/role/alembic/secret-id
```

Esses valores devem ser salvos nas pastas `vault/agent-*/auth/`.

---

## 9️⃣ Aplicação FastAPI

### Preparação local

```bash
pyenv local 3.12.8
poetry install
```

Configure o interpretador Python na sua IDE.

### Dockerfile

O Dockerfile do projeto utiliza **multi-stage build** para reduzir a imagem final e garantir isolamento das dependências.

(O Dockerfile permanece conforme definido no projeto.)

---

## 🔄 Build Automatizado

Utilize o script `build.sh`:

```bash
chmod +x ./build.sh
./build.sh
```

Esse script:

* Sobe Vault e MySQL
* Inicializa e quebra o selo do Vault
* Executa Alembic
* Sobe a API somente após os secrets estarem disponíveis

---

## 📚 Conclusão

Esse fluxo garante:

* 🔐 Segurança total das credenciais
* 🔄 Rotação automática de usuários
* ❌ Nenhuma senha fixa no código
* ☁️ Arquitetura cloud-native
* 🛡️ Aderência a Zero Trust e Least Privilege

Ideal para cenários **DevOps**, **SRE** e **ambientes produtivos**.
