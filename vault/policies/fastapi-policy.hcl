# Permite gerar credenciais dinâmicas com suporte a caminhos com barra (wildcard)
path "database/creds/fastapi-role*" {
  capabilities = ["read"]
}

# Permite ao Agent verificar as capacidades do mount (necessário para v1.21.0+)
path "sys/internal/ui/mounts/database/creds/fastapi-role*" {
  capabilities = ["read"]
}

# Opcional: Permite renovar o próprio token (ajuda na estabilidade do Agent)
path "auth/token/renew-self" {
  capabilities = ["update"]
}