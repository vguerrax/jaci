"""Prepara explicitamente um ambiente sintético, sem ler .env de produção."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

from dotenv import dotenv_values

from app.testing_environment import MARKER, PROJECT_ROOT, allowed_runtime, validate_runtime


def setup_environment(env_file: str, runtime_dir: str) -> None:
    target = Path(env_file).resolve()
    directory = Path(runtime_dir).resolve()
    if target.name != '.env.test' or not allowed_runtime(directory):
        raise ValueError('Use .env.test e um diretório isolado de testes.')
    url = f'sqlite:///{directory / "jaci.sqlite3"}'
    if any(os.environ.get(key, value) != value for key, value in {
        'DATABASE_URL': url, 'APP_ENV': 'test', 'AUTH_MOCK': 'true'
    }.items()):
        raise ValueError('Sobrescrita ambiental incompatível com ambiente isolado.')
    if directory.exists() and any(directory.iterdir()):
        validate_runtime(directory)
    elif target.exists():
        raise ValueError('Arquivo de ambiente existente sem marcador; não sobrescrever.')
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    marker = directory / MARKER
    if not marker.exists():
        marker.write_text(json.dumps({'kind': 'jaci-test-runtime-v1', 'root': str(directory)}))
    secret_file = directory / 'auth-secret'
    if not secret_file.exists():
        with secret_file.open('x') as secret:
            os.chmod(secret_file, 0o600)
            secret.write(secrets.token_urlsafe(48))
    values = {'APP_ENV': 'test', 'AUTH_MOCK': 'true', 'DATABASE_URL': url,
              'DEBUG': 'false', 'SECURE_COOKIE': 'false', 'SMTP_MOCK': 'true',
              'SMTP_USER': 'test@example.com', 'SMTP_PASSWORD': 'synthetic-only',
              'BACKUP_ENABLED': 'false', 'APP_URL': 'http://127.0.0.1:8014'}
    if target.exists():
        previous = dotenv_values(target)
        if any(previous.get(key) != values[key] for key in ('APP_ENV','AUTH_MOCK','DATABASE_URL')):
            raise ValueError('Ambiente existente incompatível; não sobrescrever.')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x') as output:
            os.chmod(target, 0o600)
            output.write(''.join(f'{key}="{value}"\n' for key,value in values.items()))
    environment = {**os.environ, 'ENV_FILE': str(target)}
    subprocess.run([sys.executable, '-m', 'scripts.apply_migrations'], cwd=PROJECT_ROOT,
                   env=environment, check=True)
    subprocess.run([sys.executable, '-m', 'scripts.seed_test_data'], cwd=PROJECT_ROOT,
                   env=environment, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', default='.env.test')
    parser.add_argument('--runtime-dir', default=str(PROJECT_ROOT/'.test-runtime/manual'))
    args = parser.parse_args()
    setup_environment(args.env_file, args.runtime_dir)


if __name__ == '__main__':
    main()
