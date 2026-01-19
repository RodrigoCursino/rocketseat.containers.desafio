exit_after_auth = true
pid_file = "/tmp/vault-agent-alembic.pid"

vault {
  address = "http://vault:8200"
}

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path   = "/vault/auth/role_id"
      secret_id_file_path = "/vault/auth/secret_id"
      remove_secret_id_file_after_reading = false # Adicione isso
    }
  }
}

template {
  source      = "/vault/templates/alembic.ctmpl"
  destination = "/vault/secrets/database.env"
  perms       = 0600
}
