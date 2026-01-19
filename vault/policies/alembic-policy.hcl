# Permite gerar credenciais dinâmicas com suporte a caminhos com barra (wildcard)
path "database/creds/alembic-role*" {
  capabilities = ["read"]
}

# Permite ao Agent verificar as capacidades do mount
path "sys/internal/ui/mounts/database/creds/alembic-role*" {
  capabilities = ["read"]
}

# Opcional: Permite renovar o próprio token
path "auth/token/renew-self" {
  capabilities = ["update"]
}