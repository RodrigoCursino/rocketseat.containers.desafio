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
docker compose up vault mysql --build -d
```

Esse comando sobe os serviços base (Vault e MySQL).

---

## 3️⃣ Inicialização e Unseal do Vault

### Acessar o container do Vault
Siga os passos dessa [documentação](configuracao_vault.md)

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
