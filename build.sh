#!/bin/bash
# Inicia os containers do Vault e do MySQL
docker compose down -v
docker compose up --build vault mysql -d

sleep 5

# Array com as suas chaves (substitua pelas chaves geradas no seu init)
KEYS=(
  #chaves do useal aqui
)

echo "Iniciando processo de Unseal do Vault..."

for KEY in "${KEYS[@]}"
do
  echo "Enviando chave de desbloqueio..."
  docker exec vault vault operator unseal "$KEY"
  sleep 1
done

echo "---"
echo "Verificando status do Vault:"
docker exec vault vault status | grep "Sealed"

echo "Processo de Unseal concluído -validando permissões de pasta."
sudo mkdir -p vault/secrets
sudo chown -R 100:100 vault/secrets
sudo chmod 750 vault/secrets
sudo chmod -R 777 vault/secrets

sleep 3

#Inicia os containers do Vault Agent
docker compose up vault-agent-alembic vault-agent-fastapi -d
sleep 10

docker compose up alembic -d
sleep 2

docker compose up fastapi -d
sleep 2

echo "Setup concluído!"