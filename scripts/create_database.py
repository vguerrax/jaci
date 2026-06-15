"""Cria o banco configurado em DATABASE_URL quando ele ainda não existe."""

from pathlib import Path

from sqlalchemy import create_engine, make_url, text

from app.config import get_settings


def create_database_if_missing(database_url: str) -> bool:
    url = make_url(database_url)
    backend = url.get_backend_name()

    if backend == "sqlite":
        already_exists = bool(
            url.database
            and url.database != ":memory:"
            and Path(url.database).expanduser().exists()
        )
        if url.database and url.database != ":memory:":
            Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(database_url)
        with engine.connect():
            pass
        engine.dispose()
        return not already_exists

    if backend != "postgresql":
        raise RuntimeError(f"Banco não suportado para criação automática: {backend}")

    database_name = url.database
    if not database_name:
        raise RuntimeError("DATABASE_URL precisa informar o nome do banco PostgreSQL.")

    admin_database = "postgres" if database_name != "postgres" else "template1"
    admin_url = url.set(database=admin_database)
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            exists = connection.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": database_name},
            )
            if exists:
                return False
            quoted_name = connection.dialect.identifier_preparer.quote(database_name)
            connection.execute(text(f"CREATE DATABASE {quoted_name}"))
            return True
    finally:
        engine.dispose()


if __name__ == "__main__":
    created = create_database_if_missing(get_settings().database_url)
    print("Banco criado." if created else "Banco já existe.")
