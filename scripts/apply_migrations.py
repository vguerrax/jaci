"""Aplica migrações Alembic e adota bancos SQLite legados."""

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database import engine, ensure_schema_compatibility


def apply_migrations() -> None:
    config = Config("alembic.ini")
    inspector = inspect(engine)
    has_app_schema = inspector.has_table("users")
    has_alembic_version = inspector.has_table("alembic_version")

    if has_app_schema and not has_alembic_version:
        if engine.dialect.name != "sqlite":
            raise RuntimeError(
                "O PostgreSQL já possui tabelas, mas não possui histórico Alembic. "
                "Valide o schema antes de marcá-lo como migrado."
            )
        ensure_schema_compatibility()
        command.stamp(config, "head")
        return

    command.upgrade(config, "head")


if __name__ == "__main__":
    apply_migrations()
