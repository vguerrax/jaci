"""Migra todos os dados do SQLite para PostgreSQL preservando IDs e relações."""

import argparse
import os
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import MetaData, create_engine, func, inspect, make_url, select, text


TABLE_ORDER = [
    "users",
    "groups",
    "group_members",
    "categories",
    "templates",
    "template_items",
    "executions",
    "execution_items",
    "notifications",
]


def normalize_postgres_target(target: str | None) -> str | None:
    """Normaliza URLs fornecidas por provedores para o driver Psycopg 3."""
    if not target:
        return target
    if target.startswith("postgres://"):
        return target.replace("postgres://", "postgresql+psycopg://", 1)
    if target.startswith("postgresql://"):
        return target.replace("postgresql://", "postgresql+psycopg://", 1)
    return target


def load_target_database_url() -> str | None:
    """Carrega DATABASE_URL exportada ou do arquivo indicado por ENV_FILE."""
    if database_url := os.getenv("DATABASE_URL"):
        return normalize_postgres_target(database_url)
    env_file = os.getenv("ENV_FILE", ".env")
    return normalize_postgres_target(dotenv_values(env_file).get("DATABASE_URL"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default="sqlite:///./data-dev/jaci.db",
        help="Caminho ou URL SQLAlchemy do SQLite de origem.",
    )
    parser.add_argument(
        "--target",
        default=load_target_database_url(),
        help="URL PostgreSQL de destino. Padrão: DATABASE_URL do ENV_FILE.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Apaga os dados existentes no destino antes da importação.",
    )
    return parser.parse_args()


def normalize_sqlite_source(source: str) -> str:
    """Converte um caminho de arquivo em uma URL SQLite SQLAlchemy."""
    if source.startswith("sqlite"):
        return source
    if "://" in source:
        raise ValueError("A origem deve ser um caminho ou banco SQLite.")
    return f"sqlite:///{Path(source).expanduser().resolve().as_posix()}"


def migrate_data(
    source_url: str, target_url: str | None, replace: bool = False
) -> dict[str, int]:
    source_url = normalize_sqlite_source(source_url)
    target_url = normalize_postgres_target(target_url)
    if not target_url or make_url(target_url).get_backend_name() != "postgresql":
        raise ValueError("O destino deve ser um banco PostgreSQL.")

    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url, pool_pre_ping=True)
    try:
        source_metadata = MetaData()
        target_metadata = MetaData()
        source_metadata.reflect(bind=source_engine)
        target_metadata.reflect(bind=target_engine)

        missing = [table for table in TABLE_ORDER if table not in target_metadata.tables]
        if missing:
            raise RuntimeError(
                "Aplique as migrações no PostgreSQL antes da importação. "
                f"Tabelas ausentes: {', '.join(missing)}"
            )

        counts: dict[str, int] = {}
        with source_engine.connect() as source, target_engine.begin() as target:
            populated = [
                table_name
                for table_name in TABLE_ORDER
                if target.scalar(
                    select(func.count()).select_from(target_metadata.tables[table_name])
                )
            ]
            if populated and not replace:
                raise RuntimeError(
                    "O destino já contém dados. Use --replace somente após confirmar "
                    f"que deseja substituir: {', '.join(populated)}"
                )

            if replace:
                for table_name in reversed(TABLE_ORDER):
                    target.execute(target_metadata.tables[table_name].delete())

            for table_name in TABLE_ORDER:
                source_table = source_metadata.tables.get(table_name)
                target_table = target_metadata.tables[table_name]
                if source_table is None:
                    counts[table_name] = 0
                    continue

                target_columns = {column.name for column in target_table.columns}
                rows = source.execute(select(source_table)).mappings().all()
                payload = [
                    {key: value for key, value in row.items() if key in target_columns}
                    for row in rows
                ]
                if payload:
                    target.execute(target_table.insert(), payload)
                counts[table_name] = len(payload)

            for table_name in TABLE_ORDER:
                table = target_metadata.tables[table_name]
                if "id" not in table.columns:
                    continue
                quoted_table = target.dialect.identifier_preparer.quote(table_name)
                target.execute(
                    text(
                        "SELECT setval("
                        "pg_get_serial_sequence(:table_name, 'id'), "
                        f"COALESCE((SELECT MAX(id) FROM {quoted_table}), 1), "
                        f"EXISTS(SELECT 1 FROM {quoted_table}))"
                    ),
                    {"table_name": table_name},
                )

        return counts
    finally:
        source_engine.dispose()
        target_engine.dispose()


if __name__ == "__main__":
    args = parse_args()
    result = migrate_data(args.source, args.target, args.replace)
    for table_name, count in result.items():
        print(f"{table_name}: {count} registro(s)")
