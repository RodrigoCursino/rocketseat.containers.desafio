# Etapa 1 - Build
FROM python:3.12-alpine AS build

# Instalar dependências básicas no Alpine
RUN apk add --no-cache curl build-base

WORKDIR /app

# Instalar poetry
ENV POETRY_VERSION=2.2.0
RUN curl -sSL https://install.python-poetry.org | python3 -
    
# Adicionar poetry ao PATH
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml .
COPY poetry.lock .
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini

# Criar venv e instalar dependências
RUN poetry config virtualenvs.in-project true && poetry install --no-root --no-interaction --no-ansi 

# Etapa 2 - Runtime
FROM python:3.12-alpine
WORKDIR /app
COPY --from=build /app .
COPY --from=build /app/.venv .venv      
ENV PATH="/app/.venv/bin:$PATH" 
# EXPOSE 3000
# CMD ["uvicorn", "src.app:api", "--host", "0.0.0.0", "--port", "3000"]

# Para buildar a imagem:
# docker build -t app-desafio-rocketseat:v1 .
# Para rodar o container:
# docker run -d --name app-desafio-rocketseat -p 3000:3000 api-desafio-rocketseat:v1