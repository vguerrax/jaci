"""Contratos BL-0026: ambiente isolado, mock e comandos públicos."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def process(code, *, env_file=None, **overrides):
    environment = {key: value for key, value in os.environ.items()
                   if key in ('PATH', 'LANG', 'HOME', 'TMPDIR')}
    environment.update(ENV_FILE=str(env_file or '/tmp/jaci-test-no-env'),
                       SMTP_USER='test@example.com', SMTP_PASSWORD='synthetic',
                       DEBUG='false')
    environment.update(overrides)
    return subprocess.run([sys.executable, '-c', code], cwd=ROOT,
                          env=environment, capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize('app_env', ['production', 'development', 'unknown'])
def test_mock_cannot_start_outside_test(app_env):
    result = process('from app.config import Settings; Settings()',
                     AUTH_MOCK='true', APP_ENV=app_env)
    assert result.returncode != 0
    assert 'AUTH_MOCK' in result.stderr or 'app_env' in result.stderr


def setup(tmp_path):
    env_file = tmp_path / '.env.test'
    runtime = tmp_path / 'jaci-test-run'
    code = ('from scripts.test_environment import setup_environment; '
            f'setup_environment({str(env_file)!r}, {str(runtime)!r})')
    result = process(code)
    assert result.returncode == 0, result.stderr
    return env_file, runtime


def test_setup_migrates_and_seeds_idempotently(tmp_path):
    env_file, runtime = setup(tmp_path)
    result = process('from scripts.seed_test_data import seed; seed(); seed(); '
                     'from app.database import SessionLocal; '
                     'from app.models import User, Group; from sqlalchemy import select,func; '
                     'db=SessionLocal(); '
                     'assert db.scalar(select(func.count()).select_from(User)) == 3; '
                     'assert db.scalar(select(func.count()).select_from(Group)) == 2',
                     env_file=env_file)
    assert result.returncode == 0, result.stderr
    assert (runtime / '.jaci-test-runtime').is_file()
    assert (runtime / 'auth-secret').stat().st_mode & 0o777 == 0o600
    assert env_file.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize('database_url', ['sqlite:////tmp/real.db',
                                         'postgresql://user:pass@localhost/production'])
def test_unsafe_database_override_is_rejected_before_connect(tmp_path, database_url):
    env_file, runtime = setup(tmp_path)
    result = process('from app.database import engine', env_file=env_file,
                     DATABASE_URL=database_url)
    assert result.returncode != 0
    assert 'isolado' in result.stderr


def test_setup_refuses_real_env_or_unowned_directory(tmp_path):
    real = tmp_path / '.env.production'
    real.write_text('KEEP=original\n')
    runtime = tmp_path / 'jaci-test-existing'
    runtime.mkdir()
    (runtime / 'keep').write_text('original')
    for env_file in [real, tmp_path / '.env.test']:
        result = process('from scripts.test_environment import setup_environment; '
                         f'setup_environment({str(env_file)!r}, {str(runtime)!r})')
        assert result.returncode != 0
    assert real.read_text() == 'KEEP=original\n'
    assert (runtime / 'keep').read_text() == 'original'


future_mock = pytest.mark.xfail(strict=True, run=False, reason='BL-0026 fatia 1.2')
future_scripts = pytest.mark.xfail(strict=True, run=False, reason='BL-0026 fatia 2.1')


def test_mock_login_refresh_restart_revocation_and_tamper(tmp_path):
    env_file, _ = setup(tmp_path)
    login = process('import asyncio,json; from app.services import tupa_auth_service as a; '
                    'print(json.dumps(asyncio.run(a.token("owner@example.com","jaci-test-only"))))',
                    env_file=env_file)
    assert login.returncode == 0, login.stderr
    tokens = json.loads(login.stdout)
    result = process(f'''import asyncio
from app.services import tupa_auth_service as a
access={tokens['access_token']!r}
refresh={tokens['refresh_token']!r}
assert a.decode_access_token(access)['email']=='owner@example.com'
assert a.decode_access_token(access+'bad') is None
new=asyncio.run(a.refresh(refresh))
assert a.decode_access_token(new['access_token']) is not None
try: asyncio.run(a.refresh(refresh))
except a.TupaError: pass
else: raise AssertionError('refresh antigo reutilizado')
from jose import jwt
from app.services.test_auth_service import _secret
expired=jwt.get_unverified_claims(new['access_token'])
expired['exp']=1
assert a.decode_access_token(jwt.encode(expired,_secret(),algorithm='HS256')) is None
asyncio.run(a.logout(new['access_token']))
assert a.decode_access_token(new['access_token']) is None
try: asyncio.run(a.refresh(new['refresh_token']))
except a.TupaError: pass
else: raise AssertionError('refresh revogado aceito')
''', env_file=env_file)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('email,password', [('unknown@example.com','jaci-test-only'),
                                           ('owner@example.com','wrong')])
def test_mock_rejects_unknown_identity_and_password(tmp_path,email,password):
    env_file,_=setup(tmp_path)
    result=process(f'''import asyncio
from app.services import tupa_auth_service as a
try: asyncio.run(a.token({email!r},{password!r}))
except a.TupaError as e: assert e.status_code==401
else: raise AssertionError('identidade aceita')
''',env_file=env_file)
    assert result.returncode==0,result.stderr


def test_mock_http_authorization_and_unsupported_operations(tmp_path):
    env_file,_=setup(tmp_path)
    result=process('''import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Group
from sqlalchemy import select
from app.services import tupa_auth_service as auth
def no_network(*args,**kwargs): raise AssertionError('rede externa')
import httpx
httpx.AsyncClient = no_network
auth._jwks = no_network
with TestClient(app) as c:
    for email in ['owner@example.com','member@example.com','outsider@example.com']:
        r=c.post('/auth/password-login',data={'email':email,'password':'jaci-test-only'})
        assert r.status_code==200,r.text
        assert c.cookies.get('jaci_session')
        assert 'Autenticação simulada' in c.get('/').text
        db=SessionLocal()
        foreign=db.scalar(select(Group).where(Group.name=='Casa B' if email!='outsider@example.com' else Group.name=='Casa A'))
        c.cookies.set('jaci_active_group',str(foreign.id))
        body=c.get('/').text
        assert 'Erro interno' not in body
        snapshot=c.get('/api/offline/snapshot').json()
        assert foreign.id not in [g['id'] for g in snapshot['groups']]
        denied=c.get('/groups/'+str(foreign.id),follow_redirects=False)
        assert denied.status_code in (302,303,403,404)
        db.close()
        assert c.get('/auth/logout').status_code==200
    try: asyncio.run(auth.create_user('new@example.com','password'))
    except auth.TupaError as e: assert e.status_code==501
    else: raise AssertionError('cadastro mock arbitrário')
''',env_file=env_file)
    assert result.returncode==0,result.stderr


@future_scripts
def test_test_runner_propagates_selection_and_exit_status(tmp_path):
    test_file=tmp_path/'test_exit.py'
    test_file.write_text('def test_selected(): assert False\n')
    result=subprocess.run(['bash','scripts/run_tests.sh','-q',str(test_file)],
                          cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==1,result.stdout+result.stderr
    assert '1 failed' in result.stdout


@future_scripts
def test_test_server_refuses_missing_env_before_start(tmp_path):
    result=subprocess.run(['bash','scripts/run_test_server.sh'],cwd=ROOT,
                          env={**os.environ,'ENV_FILE':str(tmp_path/'.env.test')},
                          capture_output=True,text=True)
    assert result.returncode!=0
    assert 'ambiente' in result.stderr.lower()


def test_real_auth_path_rejects_mock_tokens_without_network(tmp_path):
    env_file,_=setup(tmp_path)
    result=process('''import asyncio
from app.services import tupa_auth_service as a
from app.config import Settings
tokens=asyncio.run(a.token('owner@example.com','jaci-test-only'))
a.settings=Settings(auth_mock=False,tupa_product_id='test-product',_env_file=None)
def no_jwks(): raise AssertionError('mock token chegou ao JWKS real')
a._jwks=no_jwks
assert a.decode_access_token(tokens['access_token']) is None
async def request(method,path,**kwargs):
    assert method=='POST' and path=='/auth/token'
    assert kwargs['json']['product_id']=='test-product'
    return {'real_path':'unchanged'}
a._request=request
assert asyncio.run(a.token('real@example.com','password'))=={'real_path':'unchanged'}
''',env_file=env_file)
    assert result.returncode==0,result.stderr
