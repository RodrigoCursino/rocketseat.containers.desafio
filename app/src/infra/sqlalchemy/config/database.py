from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import hvac
import os
import time

# client = hvac.Client(url=os.environ["VAULT_ADDR"])

# # Login via AppRole
# def get_vault_client():
#     print("Conectando ao Vault...")
#     client = hvac.Client(url=os.environ["VAULT_ADDR"])
#     while True:
#         try:
#             if not client.sys.is_sealed():
#                 client.auth.approle.login(
#                     role_id=os.environ["VAULT_ROLE_ID"],
#                     secret_id=os.environ["VAULT_SECRET_ID"]
#                 )
#                 return client
#         except Exception as e:
#             print("Vault indisponível, tentando novamente...")
#             time.sleep(3)

# client = get_vault_client()
# creds = client.read("database/creds/fastapi-role")["data"]

from dotenv import load_dotenv
import time
import os

for _ in range(10):
    load_dotenv("/vault/secrets/database.env")
    if os.getenv("DATABASE_URL"):
        break
    time.sleep(1)
else:
    raise RuntimeError("DATABASE_URL não carregada pelo Vault Agent")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("DATABASE_URL não carregada pelo Vault Agent")

# DB_USER = creds["username"]
# DB_PASSWORD = creds["password"]
# DB_NAME = os.getenv("MYSQL_DATABASE", "appdb")
# DB_HOST = os.getenv("MYSQL_HOST", "mysql")  # nome do serviço no docker-compose
# DB_PORT = os.getenv("MYSQL_PORT", "3306")

# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    #connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()