"""Prepara explicitamente um ambiente sintético, sem ler .env de produção."""
import argparse
import json
import os
from pathlib import Path
import secrets
import signal
import shutil
import tempfile
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


def run_python_tests(arguments: list[str]) -> int:
    # A suíte Python mantém suas fixtures em memória; nunca herda .env real.
    from app.config import Settings
    directory = Path(tempfile.mkdtemp(prefix='jaci-test-python-'))
    (directory / MARKER).write_text(json.dumps(
        {'kind': 'jaci-test-runtime-v1', 'root': str(directory)}))
    env_file = directory / '.env.test'
    env_file.write_text('APP_ENV=test\nAUTH_MOCK=false\nDATABASE_URL=sqlite://\n')
    environment = {key:value for key,value in os.environ.items()
                   if key.lower() not in Settings.model_fields and key != 'ENV_FILE'}
    environment.update(ENV_FILE=str(env_file), APP_ENV='test', AUTH_MOCK='false',
                       DATABASE_URL='sqlite://', DEBUG='false', SMTP_USER='test@example.com',
                       SMTP_PASSWORD='synthetic-only', SMTP_MOCK='true', BACKUP_ENABLED='false')
    previous = signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    process = None
    try:
        process = subprocess.Popen(
            [sys.executable, '-m', 'pytest', '--ignore=tests/ui', *arguments],
            env=environment, cwd=PROJECT_ROOT, start_new_session=True)
        return process.wait()
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        signal.signal(signal.SIGTERM, previous)
        validate_runtime(directory)
        shutil.rmtree(directory)


def serve_environment(env_file: str, port: int) -> None:
    target = Path(env_file).resolve()
    if target.name != '.env.test' or not target.is_file():
        raise ValueError('Arquivo de ambiente de testes ausente; execute setup_test_env.sh.')
    os.environ['ENV_FILE'] = str(target)
    from app.config import get_settings
    settings = get_settings()
    if settings.app_env != 'test' or not settings.auth_mock:
        raise ValueError('Servidor exige ambiente test com AUTH_MOCK explícito.')
    from app.testing_environment import validate_database
    database = validate_database(settings.database_url)
    if not database.is_file() or not (database.parent/'auth-secret').is_file():
        raise ValueError('Ambiente não preparado; execute setup_test_env.sh.')
    import uvicorn
    uvicorn.run('app.main:app', host='127.0.0.1', port=port, reload=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', default='.env.test')
    parser.add_argument('--runtime-dir', default=str(PROJECT_ROOT/'.test-runtime/manual'))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--serve', action='store_true')
    mode.add_argument('--run-tests', action='store_true')
    mode.add_argument('--clean', action='store_true')
    parser.add_argument('--port', type=int, default=8014)
    parser.add_argument('test_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.run_tests:
        arguments = args.test_args[1:] if args.test_args[:1] == ['--'] else args.test_args
        sys.exit(run_python_tests(arguments))
    if args.test_args:
        parser.error('Argumentos extras só são aceitos em --run-tests.')
    if args.serve:
        serve_environment(args.env_file, args.port)
    elif args.clean:
        directory = validate_runtime(Path(args.runtime_dir))
        target = Path(args.env_file).resolve()
        values = dotenv_values(target)
        if target.name != '.env.test' or values.get('DATABASE_URL') != f'sqlite:///{directory / "jaci.sqlite3"}':
            raise ValueError('Arquivo de ambiente não corresponde ao diretório isolado.')
        shutil.rmtree(directory)
        target.unlink()
    else:
        setup_environment(args.env_file, args.runtime_dir)


if __name__ == '__main__':
    main()
