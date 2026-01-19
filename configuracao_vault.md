# Guia Completo de Configuração do Vault com Agentes (FastAPI + Alembic)

Este documento descreve **passo a passo** como configurar o **HashiCorp Vault** para fornecer **credenciais dinâmicas de MySQL** utilizando **Vault Agent + AppRole**, seguindo exatamente suas anotações, com correções conceituais, boas práticas e validações importantes.

---

## 🎯 Objetivo

Configurar o Vault para:

* Gerar **credenciais dinâmicas de MySQL**
* Isolar o Vault das aplicações usando **Vault Agent**
* Criar **dois agentes distintos**:

  * **FastAPI** → permissões CRUD
  * **Alembic** → permissões administrativas
* Utilizar **AppRole** para autenticação segura
* Renderizar secrets via **templates (.ctmpl)** em arquivos `.env`

---

## 🧠 Conceitos Fundamentais

### 🔐 O que é o Vault?

O Vault é um serviço de **gerenciamento de segredos** que permite armazenar, acessar e **gerar segredos dinamicamente**, como senhas de banco de dados com TTL.

---

### 🧩 O que é AppRole?

**AppRole** é um método de autenticação do Vault **pensado para aplicações e serviços**, não para humanos.

Uma AppRole é composta por:

* **role_id** → identifica a aplicação
* **secret_id** → funciona como uma senha

📌 A aplicação **nunca acessa o Vault diretamente**. Quem autentica é o **Vault Agent**, usando `role_id + secret_id`.

---

### 🤖 O que é Vault Agent?

O Vault Agent atua como um **sidecar** responsável por:

* Autenticar no Vault
* Renovar tokens automaticamente
* Buscar secrets
* Renderizar secrets em arquivos via templates

A aplicação apenas **consome arquivos locais**, mantendo total isolamento do Vault.

---

## 📁 Estrutura de Diretórios Recomendada

```text
vault/
├── config/
│   └── vault.hcl
├── policies/
│   ├── fastapi-policy.hcl
│   └── alembic-policy.hcl
├── templates/
│   ├── fastapi.ctmpl
│   └── alembic.ctmpl
├── agent-fastapi/
│   ├── auth/
│   │   ├── role_id
│   │   └── secret_id
│   └── secrets/
├── agent-alembic/
│   ├── auth/
│   │   ├── role_id
│   │   └── secret_id
│   └── secrets/
```

---

## 1️⃣ Configuração do Serviço Vault

Arquivo principal do Vault:

📄 `vault/config/vault.hcl`

Este arquivo define:

* Porta do serviço
* Backend de storage
* Configurações de log

Ele é usado no comando:

```bash
vault server -config=/vault/config/vault.hcl
```

---

## 2️⃣ Criação dos Vault Agents

Cada aplicação possui **seu próprio agente**, garantindo isolamento total.

### Responsabilidades do agente:

* Autenticar via AppRole
* Buscar secrets
* Gerar arquivos `.env`

Arquivos:

* `agent-fastapi.hcl`
* `agent-alembic.hcl`

📌 Cada agente deve ter:

* Pasta `auth/` → `role_id` e `secret_id`
* Pasta `secrets/` → arquivos gerados pelos templates

---

## 3️⃣ Criação dos Templates (.ctmpl)

Os templates definem **como o secret será renderizado**.

Exemplo de uso:

```hcl
template {
  source      = "/vault/templates/fastapi.ctmpl"
  destination = "/vault/secrets/database.env"
}
```

📌 O Vault Agent cria o arquivo de forma **atômica** (arquivo temporário + rename).

---

## 4️⃣ Policies (Políticas de Acesso)

As **policies** definem **o que uma aplicação pode acessar dentro do Vault**.

⚠️ Importante:

* Policies **não acessam o banco diretamente**
* Elas controlam **paths do Vault**
* Sempre associadas a uma **AppRole**

### Validação da sua definição

✔️ Correta conceitualmente
✔️ Separação entre FastAPI e Alembic está adequada

Exemplo:

```hcl
path "database/creds/fastapi-role" {
  capabilities = ["read"]
}
```

---

## 5️⃣ Inicialização do Vault

### Subir serviços base

```bash
docker compose up --build vault mysql -d
```

### Acessar o container do Vault

```bash
docker exec -it vault sh
```

---

## 🔓 Desbloqueio (Unseal) do Vault

### Inicializar o Vault

```bash
vault operator init
```

Esse comando gera:

* 5 **Unseal Keys**
* 1 **Root Token**

### Quebrar o selo

```bash
vault operator unseal <UNSEAL_KEY>
```

(repita até completar o quorum)

### Login

⚠️ Correção importante:

✅ O login deve ser feito com o **ROOT TOKEN**, não com a unseal key.

```bash
vault login <ROOT_TOKEN>
```

---

## 6️⃣ Configurando o Vault para MySQL

### Ativar o secrets engine de database

```bash
vault secrets enable database
```

Verificação:

```bash
vault secrets list
```

---

### Configurar conexão com o MySQL

```bash
vault write database/config/mysql \
  plugin_name=mysql-database-plugin \
  connection_url="{{username}}:{{password}}@tcp(mysql:3306)/" \
  allowed_roles="alembic-role,fastapi-role" \
  username="root" \
  password="root"
```

📌 `mysql` deve ser **exatamente o nome do serviço no docker-compose**.

---

## 7️⃣ Criação das Roles de Database

### FastAPI (CRUD)

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

---

### Alembic (Admin)

```bash
vault write database/roles/alembic-role \
  db_name=mysql \
  creation_statements="
    CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';
    GRANT ALL PRIVILEGES ON appdb.* TO '{{name}}'@'%';
  " \
  default_ttl=15m \
  max_ttl=1h
```

---

## 8️⃣ Associação das Policies

```bash
vault policy write alembic-policy /vault/policies/alembic-policy.hcl
vault policy write fastapi-policy /vault/policies/fastapi-policy.hcl
```

---

## 9️⃣ Configuração do AppRole

### Ativar AppRole

```bash
vault auth enable approle
```

Verificar:

```bash
vault auth list
```

---

### Criar AppRoles

#### FastAPI

```bash
vault write auth/approle/role/fastapi \
  token_policies="fastapi-policy" \
  token_ttl=1h \
  token_max_ttl=4h
```

#### Alembic

```bash
vault write auth/approle/role/alembic \
  token_policies="alembic-policy" \
  token_ttl=1h \
  token_max_ttl=4h
```

---

## 🔑 Geração de role_id e secret_id

### FastAPI

```bash
vault read auth/approle/role/fastapi/role-id
vault write -f auth/approle/role/fastapi/secret-id
```

### Alembic

```bash
vault read auth/approle/role/alembic/role-id
vault write -f auth/approle/role/alembic/secret-id
```

---

### Persistindo nos agentes

```bash
echo "<ROLE_ID>" > vault/agent-alembic/auth/role_id
echo "<SECRET_ID>" > vault/agent-alembic/auth/secret_id
```

(repita para fastapi)

---

## 🔐 Testando o login com os agentes (AppRole)

Após a criação da **AppRole** e a geração do `role_id` e `secret_id`, é possível validar se o agente consegue autenticar corretamente no Vault.

### 1️⃣ Realizar o login usando AppRole

Execute o comando abaixo, substituindo os valores pelos gerados anteriormente:

```bash
vault write auth/approle/login \
  role_id="<ROLE_ID>" \
  secret_id="<SECRET_ID>"
```
### 2️⃣ Testar o acesso às credenciais dinâmicas
Utilize o token gerado no passo anterior para solicitar credenciais dinâmicas do banco de dados:

```bash
VAULT_TOKEN="<TOKEN_GERADO_ACIMA>" \
vault read database/creds/<NOME_DA_REGRA>
```


📌 Exemplo:

```bash
VAULT_TOKEN="s.xxxxx" vault read database/creds/fastapi-role
```

O comando irá retornar:

username

password

lease_id

ttl

Essas credenciais são temporárias, respeitam o TTL definido na role e possuem apenas os privilégios configurados para a aplicação.

✅ O que esse teste valida?

✔️ A AppRole está corretamente configurada

✔️ As policies estão associadas de forma correta

✔️ O Vault consegue gerar credenciais dinâmicas no MySQL

✔️ A aplicação terá acesso apenas ao que foi permitido

## 🔁 Finalização

```bash
docker compose down -v
```

Depois execute:

```bash
./build.sh
```

---

## ✅ Conclusão

Com essa arquitetura:

* As aplicações **nunca conhecem o Vault**
* Credenciais são **rotacionadas automaticamente**
* Cada serviço tem **privilégios mínimos necessários**
* O sistema está **pronto para produção** 🚀
