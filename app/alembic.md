| Comando                                    | Descrição                           |
| ------------------------------------------ | ----------------------------------- |
| `alembic revision -m "descrição"`          | Cria uma nova migração manual       |
| `alembic revision --autogenerate -m "msg"` | Gera migração automática            |
| `alembic upgrade head`                     | Aplica todas as migrações pendentes |
| `alembic downgrade -1`                     | Reverte a última migração           |
| `alembic history`                          | Lista histórico de versões          |
