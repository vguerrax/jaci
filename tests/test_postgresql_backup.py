from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import textwrap
import time

import pytest

from app.config import Settings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKUP_SCRIPT = PROJECT_ROOT / "scripts" / "backup_database.sh"
ENTRYPOINT_SCRIPT = PROJECT_ROOT / "scripts" / "docker-entrypoint.sh"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    path.chmod(0o755)


@pytest.fixture
def fake_postgres_tools(tmp_path: Path) -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    calls_dir = tmp_path / "calls"
    bin_dir.mkdir()
    calls_dir.mkdir()

    _write_executable(
        bin_dir / "pg_dump",
        """
        #!/usr/bin/env bash
        set -euo pipefail
        printf '%s\n' "$@" > "$CALLS_DIR/pg_dump.args"
        printf '%s' "${PGSSLMODE-}" > "$CALLS_DIR/pg_dump.sslmode"
        output=""
        previous=""
        for argument in "$@"; do
            if [[ "$previous" == "--file" ]]; then
                output="$argument"
            elif [[ "$argument" == --file=* ]]; then
                output="${argument#--file=}"
            fi
            previous="$argument"
        done
        [[ -n "$output" ]]
        printf 'custom dump in progress' > "$output"
        if [[ "${FAIL_PG_DUMP:-false}" == "true" ]]; then
            exit 8
        fi
        printf 'valid custom dump' > "$output"
        """,
    )
    _write_executable(
        bin_dir / "pg_restore",
        """
        #!/usr/bin/env bash
        set -euo pipefail
        printf '%s\n' "$@" > "$CALLS_DIR/pg_restore.args"
        dump_path="${*: -1}"
        [[ -f "$dump_path" ]]
        [[ "$dump_path" == *.tmp.* ]]
        [[ ! -e "${dump_path%%.tmp.*}" ]]
        if [[ "${FAIL_PG_RESTORE:-false}" == "true" ]]; then
            exit 9
        fi
        printf 'table public.users\n'
        """,
    )
    return bin_dir, calls_dir


def _backup_environment(
    tmp_path: Path,
    fake_postgres_tools: tuple[Path, Path],
    **overrides: str,
) -> dict[str, str]:
    bin_dir, calls_dir = fake_postgres_tools
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{bin_dir}:{environment['PATH']}",
            "CALLS_DIR": str(calls_dir),
            "DATABASE_URL": "postgresql://user:secret@db.example.com:5432/jaci",
            "BACKUP_ENABLED": "true",
            "BACKUP_DIR": str(tmp_path / "backups"),
            "BACKUP_RETENTION_DAYS": "30",
            "DATABASE_SSL_MODE": "require",
            "TZ": "America/Sao_Paulo",
        }
    )
    environment.update(overrides)
    return environment


def _run_backup(environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(BACKUP_SCRIPT)],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_backup_shell_scripts_have_valid_syntax():
    for script in (BACKUP_SCRIPT, ENTRYPOINT_SCRIPT):
        subprocess.run(["bash", "-n", str(script)], check=True)


@pytest.mark.parametrize("enabled", ["false", "FALSE", "0", "no"])
def test_backup_disabled_exits_without_calling_postgres_tools(
    tmp_path: Path,
    fake_postgres_tools: tuple[Path, Path],
    enabled: str,
):
    _, calls_dir = fake_postgres_tools
    result = _run_backup(
        _backup_environment(tmp_path, fake_postgres_tools, BACKUP_ENABLED=enabled)
    )

    assert result.returncode == 0
    assert "desabilitado" in result.stdout.lower()
    assert not (calls_dir / "pg_dump.args").exists()


def test_sqlite_is_explicitly_ignored(
    tmp_path: Path,
    fake_postgres_tools: tuple[Path, Path],
):
    _, calls_dir = fake_postgres_tools
    result = _run_backup(
        _backup_environment(
            tmp_path,
            fake_postgres_tools,
            DATABASE_URL="sqlite:///./data-dev/jaci.db",
        )
    )

    assert result.returncode == 0
    assert "sqlite" in result.stdout.lower()
    assert "ignorado" in result.stdout.lower()
    assert not (calls_dir / "pg_dump.args").exists()


@pytest.mark.parametrize("retention", ["", "0", "-1", "3.5", "thirty"])
def test_invalid_retention_fails_before_creating_a_dump(
    tmp_path: Path,
    fake_postgres_tools: tuple[Path, Path],
    retention: str,
):
    _, calls_dir = fake_postgres_tools
    result = _run_backup(
        _backup_environment(
            tmp_path,
            fake_postgres_tools,
            BACKUP_RETENTION_DAYS=retention,
        )
    )

    assert result.returncode != 0
    assert "BACKUP_RETENTION_DAYS" in result.stderr
    assert not (calls_dir / "pg_dump.args").exists()
    assert not list((tmp_path / "backups").glob("*"))


@pytest.mark.parametrize(
    ("database_url", "normalized_url"),
    [
        (
            "postgres://user:secret@db.example.com:5432/jaci",
            "postgresql://user:secret@db.example.com:5432/jaci",
        ),
        (
            "postgresql://user:secret@db.example.com:5432/jaci",
            "postgresql://user:secret@db.example.com:5432/jaci",
        ),
        (
            "postgresql+psycopg://user:secret@db.example.com:5432/jaci",
            "postgresql://user:secret@db.example.com:5432/jaci",
        ),
    ],
)
def test_backup_normalizes_postgres_urls_and_publishes_a_valid_private_dump(
    tmp_path: Path,
    fake_postgres_tools: tuple[Path, Path],
    database_url: str,
    normalized_url: str,
):
    _, calls_dir = fake_postgres_tools
    backup_dir = tmp_path / "backups"
    result = _run_backup(
        _backup_environment(
            tmp_path,
            fake_postgres_tools,
            DATABASE_URL=database_url,
        )
    )

    assert result.returncode == 0, result.stderr
    dump_arguments = (calls_dir / "pg_dump.args").read_text(encoding="utf-8").splitlines()
    assert "--format=custom" in dump_arguments
    assert "--no-owner" in dump_arguments
    assert "--no-acl" in dump_arguments
    assert normalized_url in dump_arguments
    assert (calls_dir / "pg_dump.sslmode").read_text(encoding="utf-8") == "require"

    dumps = list(backup_dir.glob("jaci_*.dump"))
    assert len(dumps) == 1
    assert stat.S_IMODE(backup_dir.stat().st_mode) == 0o700
    assert stat.S_IMODE(dumps[0].stat().st_mode) == 0o600
    assert dumps[0].read_text(encoding="utf-8") == "valid custom dump"
    assert not list(backup_dir.glob("*.tmp.*"))


def test_failed_validation_removes_temporary_dump_and_publishes_nothing(
    tmp_path: Path,
    fake_postgres_tools: tuple[Path, Path],
):
    backup_dir = tmp_path / "backups"
    result = _run_backup(
        _backup_environment(
            tmp_path,
            fake_postgres_tools,
            FAIL_PG_RESTORE="true",
        )
    )

    assert result.returncode != 0
    assert not list(backup_dir.glob("jaci_*.dump"))
    assert not list(backup_dir.glob("*.tmp.*"))


def test_failed_dump_removes_partial_temporary_file(
    tmp_path: Path,
    fake_postgres_tools: tuple[Path, Path],
):
    backup_dir = tmp_path / "backups"
    result = _run_backup(
        _backup_environment(
            tmp_path,
            fake_postgres_tools,
            FAIL_PG_DUMP="true",
        )
    )

    assert result.returncode != 0
    assert not list(backup_dir.glob("jaci_*.dump"))
    assert not list(backup_dir.glob("*.tmp.*"))


def test_retention_removes_only_expired_jaci_dumps(
    tmp_path: Path,
    fake_postgres_tools: tuple[Path, Path],
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    expired_dump = backup_dir / "jaci_20260101_023000.dump"
    recent_dump = backup_dir / "jaci_20260722_023000.dump"
    unrelated_dump = backup_dir / "potira_20260101_023000.dump"
    temporary_dump = backup_dir / "jaci_20260101_023000.dump.tmp.abandoned"
    for path in (expired_dump, recent_dump, unrelated_dump, temporary_dump):
        path.write_text("keep or remove", encoding="utf-8")
    expired_time = time.time() - (32 * 24 * 60 * 60)
    os.utime(expired_dump, (expired_time, expired_time))
    os.utime(unrelated_dump, (expired_time, expired_time))
    os.utime(temporary_dump, (expired_time, expired_time))

    result = _run_backup(_backup_environment(tmp_path, fake_postgres_tools))

    assert result.returncode == 0, result.stderr
    assert not expired_dump.exists()
    assert recent_dump.exists()
    assert unrelated_dump.exists()
    assert temporary_dump.exists()


def test_entrypoint_starts_cron_only_for_the_server_and_limits_cron_environment(
    tmp_path: Path,
):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    cron_marker = tmp_path / "cron-called"
    python_marker = tmp_path / "python-called"
    cron_environment = tmp_path / "backup.env"
    _write_executable(
        bin_dir / "cron",
        f"#!/usr/bin/env bash\nprintf called > {cron_marker!s}\n",
    )
    _write_executable(
        bin_dir / "python",
        f"#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" > {python_marker!s}\n",
    )
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{bin_dir}:{environment['PATH']}",
            "BACKUP_CRON_ENV_FILE": str(cron_environment),
            "DATABASE_URL": (
                "postgresql+psycopg://user:p@ss@db.example.com:5432/jaci"
            ),
            "BACKUP_ENABLED": "true",
            "BACKUP_DIR": "/var/backups/jaci",
            "BACKUP_RETENTION_DAYS": "30",
            "DATABASE_SSL_MODE": "verify-full",
            "TZ": "America/Sao_Paulo",
            "UNRELATED_SECRET": "must-not-reach-cron",
        }
    )

    subprocess.run(
        ["bash", str(ENTRYPOINT_SCRIPT), "python", "-m", "scripts.apply_migrations"],
        env=environment,
        check=True,
    )
    assert not cron_marker.exists()
    assert not cron_environment.exists()

    subprocess.run(
        ["bash", str(ENTRYPOINT_SCRIPT), "python", "run.py", "--no-restart"],
        env=environment,
        check=True,
    )

    assert cron_marker.exists()
    assert python_marker.exists()
    assert stat.S_IMODE(cron_environment.stat().st_mode) == 0o600
    content = cron_environment.read_text(encoding="utf-8")
    for variable in (
        "DATABASE_URL",
        "BACKUP_ENABLED",
        "BACKUP_DIR",
        "BACKUP_RETENTION_DAYS",
        "DATABASE_SSL_MODE",
        "TZ",
    ):
        assert f"{variable}=" in content
    assert "UNRELATED_SECRET" not in content
    assert "must-not-reach-cron" not in content


def test_entrypoint_delivers_backup_defaults_when_optional_variables_are_unset(
    tmp_path: Path,
):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    cron_environment = tmp_path / "backup.env"
    _write_executable(bin_dir / "cron", "#!/usr/bin/env bash\nexit 0\n")
    _write_executable(bin_dir / "python", "#!/usr/bin/env bash\nexit 0\n")
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{bin_dir}:{environment['PATH']}",
            "BACKUP_CRON_ENV_FILE": str(cron_environment),
            "DATABASE_URL": "postgresql://user:secret@db.example.com:5432/jaci",
        }
    )
    for variable in (
        "BACKUP_ENABLED",
        "BACKUP_DIR",
        "BACKUP_RETENTION_DAYS",
        "DATABASE_SSL_MODE",
        "TZ",
    ):
        environment.pop(variable, None)

    subprocess.run(
        ["bash", str(ENTRYPOINT_SCRIPT), "python", "run.py", "--no-restart"],
        env=environment,
        check=True,
    )

    loaded_environment = subprocess.run(
        [
            "bash",
            "-c",
            'source "$1"; printf "%s\\n" "$BACKUP_ENABLED" "$BACKUP_DIR" '
            '"$BACKUP_RETENTION_DAYS" "$TZ"',
            "bash",
            str(cron_environment),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert loaded_environment == [
        "true",
        "/var/backups/jaci",
        "30",
        "America/Sao_Paulo",
    ]


def test_container_configures_daily_backup_and_persistent_host_storage():
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
    cron_schedule = (PROJECT_ROOT / "deploy" / "jaci-backup.cron").read_text(
        encoding="utf-8"
    )
    compose = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    for package in ("cron", "postgresql-client", "tzdata"):
        assert package in dockerfile
    assert "America/Sao_Paulo" in dockerfile
    assert 'ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]' in dockerfile
    assert "30 2 * * *" in cron_schedule
    assert "/app/scripts/backup_database.sh" in cron_schedule
    assert "/var/log/backup.log" in cron_schedule
    assert "/opt/jaci/backups:/var/backups/jaci" in compose


def test_backup_settings_are_loaded_from_dotenv(tmp_path: Path, monkeypatch):
    env_file = tmp_path / ".env.production"
    env_file.write_text(
        "\n".join(
            [
                "DATABASE_URL=postgresql://user:secret@db.example.com:5432/jaci",
                "BACKUP_ENABLED=false",
                "BACKUP_DIR=/custom/backups",
                "BACKUP_RETENTION_DAYS=45",
                "DATABASE_SSL_MODE=verify-full",
            ]
        ),
        encoding="utf-8",
    )
    for variable in (
        "DATABASE_URL",
        "BACKUP_ENABLED",
        "BACKUP_DIR",
        "BACKUP_RETENTION_DAYS",
        "DATABASE_SSL_MODE",
    ):
        monkeypatch.delenv(variable, raising=False)

    settings = Settings(_env_file=env_file)

    assert settings.database_url.startswith("postgresql+psycopg://")
    assert settings.backup_enabled is False
    assert settings.backup_dir == "/custom/backups"
    assert settings.backup_retention_days == 45
    assert settings.database_ssl_mode == "verify-full"
