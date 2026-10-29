"""Executa Chromium com servidor e banco exclusivos; nunca usa servidor existente."""
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from uuid import uuid4

from dotenv import dotenv_values
import httpx

from app.testing_environment import MARKER, PROJECT_ROOT, validate_database, validate_runtime


def _stop(process):
    if process is not None and process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def write_result(artifacts: Path, run_id: str, status: str) -> None:
    # Playwright remove o output vazio em execuções aprovadas.
    artifacts.mkdir(parents=True, exist_ok=True)
    for path in artifacts.rglob('*'):
        if path.is_file() and path.suffix != '.png':
            path.unlink()
    (artifacts/'result.json').write_text(json.dumps({'run_id':run_id,'status':status}))


def run(arguments: list[str]) -> int:
    if os.environ.get('UI_TEST_WORKERS', '1') != '1':
        raise ValueError('UI_TEST_WORKERS deve ser 1: isolamento paralelo ainda não implementado.')
    source = Path(os.environ.get('ENV_FILE','.env.test')).resolve()
    if source.name != '.env.test' or not source.is_file():
        raise ValueError('Arquivo de ambiente de testes ausente; execute setup_test_env.sh.')
    values = dotenv_values(source)
    if values.get('APP_ENV') != 'test' or values.get('AUTH_MOCK','').lower() != 'true':
        raise ValueError('Arquivo de ambiente deve habilitar APP_ENV=test e AUTH_MOCK=true.')
    validate_database(values.get('DATABASE_URL',''))
    from scripts.setup_ui_assets import CACHE, MANIFEST
    import hashlib
    for asset in json.loads(MANIFEST.read_text()):
        cached=CACHE/asset['name']
        if not cached.is_file() or hashlib.sha256(cached.read_bytes()).hexdigest()!=asset['sha256']:
            raise ValueError('Assets UI ausentes/divergentes; execute python -m scripts.setup_ui_assets.')
    from app.config import Settings
    environment = {key:value for key,value in os.environ.items()
                   if key.lower() not in Settings.model_fields and key != 'ENV_FILE'}
    directory = Path(tempfile.mkdtemp(prefix='jaci-test-ui-'))
    run_id = uuid4().hex
    artifacts = PROJECT_ROOT/'reports/playwright'/run_id
    artifacts.mkdir(parents=True)
    environment.update(ENV_FILE=str(directory/'.env.test'))
    environment.setdefault('PLAYWRIGHT_BROWSERS_PATH', str(PROJECT_ROOT/'.cache/playwright'))
    server = tests = None
    previous = signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    status = 'interrupted'
    try:
        subprocess.run([sys.executable,'-m','scripts.test_environment',
                        '--env-file',str(directory/'.env.test'),'--runtime-dir',str(directory)],
                       cwd=PROJECT_ROOT,env=environment,check=True,
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=60)
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',0))
            port = probe.getsockname()[1]
        base_url = f'http://127.0.0.1:{port}'
        environment.update(JACI_RUN_PLAYWRIGHT='1', JACI_UI_RUN_ID=run_id,
                           PLAYWRIGHT_BASE_URL=base_url)
        server = subprocess.Popen(
            [sys.executable,'-m','scripts.test_environment','--serve',
             '--env-file',str(directory/'.env.test'),'--port',str(port)],
            cwd=PROJECT_ROOT,env=environment,start_new_session=True,
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        deadline = time.monotonic()+30
        with httpx.Client(trust_env=False,timeout=1) as client:
            while time.monotonic()<deadline:
                if server.poll() is not None:
                    raise RuntimeError('Servidor de testes encerrou antes de health.')
                try:
                    response=client.get(base_url+'/health')
                    if response.status_code==200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(.1)
            else:
                raise RuntimeError('Timeout aguardando health do servidor de testes.')
        paths = [arg.split('::',1)[0] for arg in arguments
                 if arg.startswith('tests/ui') or arg.startswith(str(PROJECT_ROOT/'tests/ui'))]
        selected = arguments if paths else ['tests/ui',*arguments]
        tests = subprocess.Popen([sys.executable,'-m','pytest',*selected,
            '--browser=chromium',f'--output={artifacts}',
            '--screenshot=only-on-failure','--video=off','--tracing=off'],
            cwd=PROJECT_ROOT,env=environment,start_new_session=True)
        result = tests.wait()
        status = 'passed' if result==0 else 'failed'
        return result
    finally:
        _stop(tests)
        _stop(server)
        signal.signal(signal.SIGTERM,previous)
        try:
            write_result(artifacts, run_id, status)
        finally:
            if (directory/MARKER).exists():
                validate_runtime(directory)
                shutil.rmtree(directory)
            elif not any(directory.iterdir()):
                directory.rmdir()
        print(f'Artifacts sintéticos: {artifacts}')


if __name__ == '__main__':
    try:
        sys.exit(run(sys.argv[1:]))
    except (ValueError,RuntimeError,subprocess.SubprocessError) as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(1)
