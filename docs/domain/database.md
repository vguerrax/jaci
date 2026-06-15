# Estratégia de Banco de Dados

## Ambientes

* Desenvolvimento usa SQLite para reduzir atrito local.
* Produção usa PostgreSQL gerenciado em nuvem.
* A variável `DATABASE_URL` é a única fonte de configuração do banco.

Exemplos:

```env
DATABASE_URL=sqlite:///./data-dev/jaci.db
DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/jaci
```

URLs fornecidas como `postgres://` ou `postgresql://` são normalizadas para o
driver Psycopg 3.

## Migrações

Alembic é a fonte de verdade do esquema. O import da aplicação não cria nem altera
tabelas.

* `python -m scripts.create_database` cria o banco quando necessário.
* `python -m scripts.apply_migrations` aplica migrações pendentes.
* `run.py` aplica migrações antes de iniciar.
* `publish.sh` cria o banco e aplica migrações antes de publicar.

SQLites legados sem tabela `alembic_version` recebem os ajustes de compatibilidade
anteriores e são marcados na revisão inicial.

## Migração de Dados

O script `scripts.migrate_sqlite_to_postgres` copia as tabelas em ordem de
dependência, preserva IDs e reajusta sequences PostgreSQL. A origem pode ser
informada como caminho de arquivo ou URL `sqlite:///`.

Por segurança, o destino precisa:

* estar com migrações atualizadas;
* estar vazio, salvo quando `--replace` for informado explicitamente.
