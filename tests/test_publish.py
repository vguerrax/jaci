import os
from pathlib import Path
import stat
import subprocess

import pytest


PUBLISH = Path(__file__).resolve().parents[1] / "publish.sh"


@pytest.fixture
def publication(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker = bin_dir / "docker"
    docker.write_text(
        '#!/usr/bin/env bash\n'
        'printf "%s\\n" "$APP_VERSION|$ENV_FILE|$*" >> "$CALLS"\n'
        'grep -Eq "^APP_VERSION=$APP_VERSION([[:space:]]|$)" "$ENV_FILE" || exit 19\n'
        'if [[ "${FAIL_DOCKER:-}" == true ]]; then exit 23; fi\n'
    )
    docker.chmod(0o755)
    calls = tmp_path / "docker.calls"
    environment = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "CALLS": str(calls),
        "APP_VERSION": "old-shell-version",
    }

    def run(*args, **overrides):
        return subprocess.run(
            ["bash", str(PUBLISH), *args], cwd=tmp_path,
            env={**environment, **overrides}, capture_output=True, text=True,
        )

    return tmp_path, calls, run


@pytest.mark.parametrize("args", [(), ("",), ("invalid",), ("1.3",),
                                 ("1.3.0\nBAD=value",), ("1.3.0", "env", "extra")])
def test_invalid_arguments_never_modify_environment_or_call_docker(publication, args):
    root, calls, run = publication
    env = root / ".env.production"
    env.write_text("APP_VERSION=old\n")

    result = run(*args)

    assert result.returncode != 0
    assert "Uso:" in result.stderr
    assert env.read_text() == "APP_VERSION=old\n"
    assert not calls.exists()


@pytest.mark.parametrize("initial", [
    "APP_VERSION=1.0.0\n",
    "",
    "OTHER=value",
    " export APP_VERSION = '1.0.0' # keep version comment\nAPP_VERSION=stale\n",
])
def test_version_is_persisted_before_all_compose_steps(publication, initial):
    root, calls, run = publication
    env = root / ".env.production"
    preserved = "# APP_VERSION=comment\nTOKEN='synthetic $(touch SHOULD_NOT_EXIST)'\n"
    env.write_text(preserved + initial)
    env.chmod(0o640)

    result = run("v1.3.0")

    assert result.returncode == 0, result.stderr
    content = env.read_text()
    assert content.startswith(preserved)
    assert content.count("APP_VERSION=1.3.0") == 1
    assert "stale" not in content
    if "# keep version comment" in initial:
        assert "# keep version comment" in content
    assert stat.S_IMODE(env.stat().st_mode) == 0o640
    assert not (root / "SHOULD_NOT_EXIST").exists()
    assert "synthetic" not in result.stdout + result.stderr
    lines = calls.read_text().splitlines()
    assert len(lines) == 4
    for line, command in zip(lines, ["build", "run --rm jaci python -m scripts.create_database",
                                    "run --rm jaci python -m scripts.apply_migrations",
                                    "up -d --remove-orphans"]):
        assert line == f"1.3.0|.env.production|compose --env-file .env.production {command}"
    assert not list(root.glob(".env.production.*"))


def test_custom_environment_path_with_spaces(publication):
    root, calls, run = publication
    env = root / "custom environment.env"
    env.write_text("APP_VERSION=old\n")

    result = run("1.3.0", str(env))

    assert result.returncode == 0, result.stderr
    assert env.read_text() == "APP_VERSION=1.3.0\n"
    assert not (root / ".env.production").exists()
    assert all(f"|{env}|" in line for line in calls.read_text().splitlines())


def test_missing_environment_aborts_before_docker(publication):
    root, calls, run = publication
    assert run("1.3.0").returncode != 0
    assert not (root / ".env.production").exists()
    assert not calls.exists()


def test_read_only_environment_aborts_before_docker(publication):
    root, calls, run = publication
    env = root / ".env.production"
    env.write_text("APP_VERSION=old\n")
    env.chmod(0o400)
    assert run("1.3.0").returncode != 0
    assert env.read_text() == "APP_VERSION=old\n"
    assert not calls.exists()


def test_failed_temporary_write_preserves_original_and_cleans_up(publication):
    root, calls, run = publication
    env = root / ".env.production"
    env.write_text("APP_VERSION=old\n")
    blocked = root / "blocked"
    blocked.mkdir()
    env.rename(blocked / env.name)
    blocked.chmod(0o500)
    try:
        result = run("1.3.0", str(blocked / env.name))
        assert result.returncode != 0
        assert (blocked / env.name).read_text() == "APP_VERSION=old\n"
        assert not calls.exists()
        assert list(blocked.iterdir()) == [blocked / env.name]
    finally:
        blocked.chmod(0o700)


def test_docker_failure_stops_sequence_and_retains_requested_version(publication):
    root, calls, run = publication
    env = root / ".env.production"
    env.write_text("APP_VERSION=old\n")

    result = run("1.3.0", FAIL_DOCKER="true")

    assert result.returncode == 23
    assert env.read_text() == "APP_VERSION=1.3.0\n"
    assert len(calls.read_text().splitlines()) == 1
