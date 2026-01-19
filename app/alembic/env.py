from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
import time
from dotenv import load_dotenv

# Caminho para o diretório 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

for _ in range(10):
    load_dotenv("/vault/secrets/database.env")
    if os.getenv("DATABASE_URL"):
        break
    time.sleep(1) 
else:
    raise RuntimeError("DATABASE_URL não carregada pelo Vault Agent")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

from src.infra.sqlalchemy.config.database import Base
import src.infra.sqlalchemy.models as models  # importa os modelos

# Configurações do Alembic
config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Executa migrações no modo offline."""
    url = SQLALCHEMY_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Executa migrações no modo online."""
    connectable = engine_from_config(
        {"sqlalchemy.url": SQLALCHEMY_DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()