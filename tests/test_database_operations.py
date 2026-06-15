import subprocess
import sys
import os

from sqlalchemy import inspect

from app.database import create_database_engine
from app.config import Settings
from scripts.create_database import create_database_if_missing


def test_database_engine_uses_sqlite_specific_connection_options(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'dev.db'}"

    engine = create_database_engine(database_url)

    assert engine.dialect.name == "sqlite"
    assert engine.pool._pre_ping is True
    engine.dispose()


def test_cloud_postgres_urls_are_normalized_to_psycopg_driver():
    settings = Settings(
        database_url="postgresql://user:secret@db.example.com:5432/jaci",
        _env_file=None,
    )

    assert settings.database_url.startswith("postgresql+psycopg://")


def test_create_database_is_idempotent_for_sqlite(tmp_path):
    database = tmp_path / "nested" / "jaci.db"
    database_url = f"sqlite:///{database}"

    assert create_database_if_missing(database_url) is True
    assert create_database_if_missing(database_url) is False
    assert database.exists()


def test_migrations_create_schema_in_empty_sqlite_database(tmp_path):
    database = tmp_path / "new.db"
    env = {
        "DATABASE_URL": f"sqlite:///{database}",
        "DEBUG": "false",
        "ENV_FILE": str(tmp_path / "missing.env"),
    }

    subprocess.run(
        [sys.executable, "-m", "scripts.apply_migrations"],
        check=True,
        env=env,
    )

    engine = create_database_engine(env["DATABASE_URL"])
    inspector = inspect(engine)
    assert inspector.has_table("users")
    assert inspector.has_table("executions")
    assert inspector.has_table("alembic_version")
    engine.dispose()


def test_initial_migration_matches_current_models(tmp_path):
    database = tmp_path / "check.db"
    env = {
        "DATABASE_URL": f"sqlite:///{database}",
        "DEBUG": "false",
        "ENV_FILE": str(tmp_path / "missing.env"),
    }
    subprocess.run(
        [sys.executable, "-m", "scripts.apply_migrations"],
        check=True,
        env=env,
    )

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "check"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    assert "No new upgrade operations detected" in result.stdout


def test_run_command_documents_port_restart_and_environment_options():
    result = subprocess.run(
        [sys.executable, "run.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "--port" in result.stdout
    assert "--restart" in result.stdout
    assert "--no-restart" in result.stdout
    assert "--env-file" in result.stdout


def test_sqlite_to_postgres_migrator_rejects_invalid_databases():
    from scripts.migrate_sqlite_to_postgres import migrate_data

    try:
        migrate_data("postgresql://source/test", "postgresql://target/test")
    except ValueError as error:
        assert str(error) == "A origem deve ser um caminho ou banco SQLite."
    else:
        raise AssertionError("Uma origem não SQLite deveria ser recusada.")


def test_sqlite_to_postgres_migrator_accepts_source_file_path(tmp_path):
    from scripts.migrate_sqlite_to_postgres import normalize_sqlite_source

    database = tmp_path / "jaci.db"

    assert normalize_sqlite_source(str(database)) == f"sqlite:///{database}"
    assert normalize_sqlite_source("sqlite:///./jaci.db") == "sqlite:///./jaci.db"


def test_sqlite_to_postgres_migrator_loads_target_from_env_file(tmp_path):
    env_file = tmp_path / ".env.production"
    env_file.write_text(
        "DATABASE_URL=postgresql://user:secret@db.example.com:5432/jaci\n",
        encoding="ascii",
    )
    env = os.environ.copy()
    env.pop("DATABASE_URL", None)
    env["DEBUG"] = "release"
    env["ENV_FILE"] = str(env_file)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from scripts.migrate_sqlite_to_postgres import parse_args; "
            "print(parse_args().target)",
        ],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == (
        "postgresql+psycopg://user:secret@db.example.com:5432/jaci"
    )


def test_sqlite_to_postgres_migrator_accepts_psycopg_target(monkeypatch):
    import scripts.migrate_sqlite_to_postgres as migrator

    class StopAfterValidation(Exception):
        pass

    def fake_create_engine(url, **kwargs):
        if url.startswith("sqlite"):
            return object()
        assert url == "postgresql+psycopg://user:secret@db.example.com:5432/jaci"
        raise StopAfterValidation

    monkeypatch.setattr(migrator, "create_engine", fake_create_engine)

    try:
        migrator.migrate_data(
            "sqlite:///source.db",
            "postgresql+psycopg://user:secret@db.example.com:5432/jaci",
        )
    except StopAfterValidation:
        pass
    else:
        raise AssertionError("A URL Psycopg deveria passar pela validação.")
