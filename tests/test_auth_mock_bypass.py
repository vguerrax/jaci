"""BL-0028: bypass usa identidade local, preservando autorização e sessões."""
import asyncio
import tempfile
from html.parser import HTMLParser

import pytest
from jose import jwt
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.config import Settings
from app.models import User, Group


@pytest.mark.parametrize('database_url', ['sqlite://', 'sqlite:///ordinary.db',
    'postgresql://user:synthetic@localhost/example'])
@pytest.mark.parametrize('env_file', ['', '/not-present/development.env'])
def test_two_flags_enable_mock_without_special_environment(monkeypatch, database_url, env_file):
    monkeypatch.setenv('ENV_FILE', env_file)
    settings = Settings(_env_file=None, app_env='test', auth_mock=True, database_url=database_url)
    assert settings.auth_mock


@pytest.fixture
def mock_auth(db, tmp_path, monkeypatch):
    from app import config, database, main
    from app.services import test_auth_service as mock, tupa_auth_service as tupa
    settings = Settings(_env_file=None, app_env='test', auth_mock=True, database_url='sqlite://',
                        smtp_user='test@example.com', smtp_password='synthetic-only')
    monkeypatch.setattr(config, 'get_settings', lambda: settings)
    monkeypatch.setattr(mock, 'get_settings', lambda: settings)
    monkeypatch.setattr(tempfile, 'gettempdir', lambda: str(tmp_path))
    monkeypatch.setattr(mock, 'tempfile', tempfile, raising=False)
    from app.services import auth_service
    monkeypatch.setattr(auth_service, 'get_settings', lambda: settings, raising=False)
    monkeypatch.setattr(tupa, 'settings', settings)
    monkeypatch.setattr(database, 'SessionLocal', lambda: Session(db.get_bind()))
    def no_network(*args, **kwargs):
        raise AssertionError('Tupã não deve ser consultado no bypass')
    monkeypatch.setattr(tupa, '_request', no_network)
    monkeypatch.setattr(tupa, '_jwks', no_network)
    return mock, tupa


@pytest.mark.parametrize('password', ['', 'qualquer valor'])
@pytest.mark.parametrize('tupa_id', [None, 'identidade-tupa-preservada'])
def test_local_user_logs_in_without_password_or_tupa_link(
    db, make_user, make_group, mock_auth, password, tupa_id
):
    from app.services.auth_service import authenticate_with_password
    _, tupa = mock_auth
    user = make_user('local@example.com')
    user.tupa_user_id = tupa_id
    user.password_hash = 'hash-legado-preservado'
    group = make_group(owner=user)
    db.commit()
    identity, tokens = asyncio.run(authenticate_with_password(db, ' LOCAL@example.com ', password))
    assert identity.id == user.id
    assert tupa.decode_access_token(tokens['access_token'])['sub'] == str(user.id)
    db.expire_all()
    assert user.tupa_user_id == tupa_id
    assert user.password_hash == 'hash-legado-preservado'
    assert [g.id for g in user.groups] == [group.id]
    assert db.scalar(select(func.count()).select_from(User)) == 1
    assert db.scalar(select(func.count()).select_from(Group)) == 1
    assert user.last_login_at is not None


def test_unknown_or_inactive_user_never_created(db, make_user, mock_auth):
    _, tupa = mock_auth
    inactive = make_user('inactive@example.com')
    inactive.is_active = False
    db.commit()
    for email in ['unknown@example.com', inactive.email]:
        with pytest.raises(tupa.TupaError) as error:
            asyncio.run(tupa.token(email, ''))
        assert error.value.status_code == 401
    assert db.scalar(select(func.count()).select_from(User)) == 1


def test_http_ws_and_middleware_use_local_identity_and_group_authorization(
    db, make_user, make_group, mock_auth, monkeypatch
):
    from app import main
    from app.dependencies import get_current_user, get_current_user_ws, get_active_group
    from app.services import notification_service
    from fastapi import Response
    _, tupa = mock_auth
    user = make_user('buyer@example.com')
    own = make_group(owner=user)
    foreign = make_group('Outra casa')
    tokens = asyncio.run(tupa.token(user.email, ''))
    request = Request({'type':'http', 'headers':[(b'cookie',
        f'jaci_session={tokens["access_token"]}; jaci_active_group={foreign.id}'.encode())]})
    assert asyncio.run(get_current_user(request, db)).id == user.id
    assert asyncio.run(get_current_user_ws(db, tokens['access_token'])).id == user.id
    assert asyncio.run(get_active_group(request, db, user)).id == own.id
    monkeypatch.setattr(main, 'SessionLocal', lambda: Session(db.get_bind()))
    monkeypatch.setattr(notification_service, 'get_unread_count', lambda _db, uid: uid)
    async def next_handler(_request):
        return Response()
    asyncio.run(main.add_unread_count(request, next_handler))
    assert request.state.unread_count == user.id


def test_mock_sessions_expire_rotate_revoke_and_recheck_activity(db, make_user, mock_auth):
    mock, tupa = mock_auth
    user = make_user('session@example.com')
    tokens = asyncio.run(tupa.token(user.email, ''))
    assert tupa.decode_access_token(tokens['access_token']+'bad') is None
    payload = jwt.get_unverified_claims(tokens['access_token'])
    payload['exp'] = 1
    assert tupa.decode_access_token(jwt.encode(payload, mock._secret(), algorithm='HS256')) is None
    renewed = asyncio.run(tupa.refresh(tokens['refresh_token']))
    assert tupa.decode_access_token(tokens['access_token']) is None
    with pytest.raises(tupa.TupaError):
        asyncio.run(tupa.refresh(tokens['refresh_token']))
    user.is_active = False
    db.commit()
    assert tupa.decode_access_token(renewed['access_token']) is None
    with pytest.raises(tupa.TupaError):
        asyncio.run(tupa.refresh(renewed['refresh_token']))
    user.is_active = True
    db.commit()
    asyncio.run(tupa.logout(renewed['access_token']))
    assert tupa.decode_access_token(renewed['access_token']) is None
    with pytest.raises(tupa.TupaError):
        asyncio.run(tupa.refresh(renewed['refresh_token']))


future_form = pytest.mark.xfail(strict=True, reason='BL-0028 fatia 1.2: formulário')


@future_form
def test_mock_http_login_accepts_missing_password_and_user_without_groups(
    db, make_user, mock_auth, monkeypatch
):
    from app.main import app
    from app.database import get_db
    from app.routers import auth
    from fastapi.testclient import TestClient
    user = make_user('alone@example.com')
    monkeypatch.setattr(auth, 'settings', mock_auth[1].settings)
    app.dependency_overrides[get_db] = lambda: db
    try:
        with TestClient(app) as client:
            result = client.post('/auth/password-login', data={'email':user.email})
            assert result.status_code == 200
            assert client.cookies.get('jaci_session')
            assert client.get('/api/offline/snapshot').json()['groups'] == []
    finally:
        app.dependency_overrides.pop(get_db, None)


@future_form
def test_mock_form_password_optional_while_real_form_requires_it(monkeypatch):
    class PasswordField(HTMLParser):
        required = None
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'input' and attrs.get('name') == 'password':
                self.required = 'required' in attrs
    from app.main import app, templates
    for enabled in [True, False]:
        html = templates.get_template('pages/login.html').render(
            request=Request({'type':'http','app':app}), user=None, auth_mock_enabled=enabled)
        field = PasswordField()
        field.feed(html)
        assert field.required is not enabled


def test_real_login_still_requires_password(db, monkeypatch):
    from app.main import app
    from app.database import get_db
    from fastapi.testclient import TestClient
    app.dependency_overrides[get_db] = lambda: db
    try:
        with TestClient(app) as client:
            assert client.post('/auth/password-login', data={'email':'x@example.com'}).status_code == 422
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_mock_application_needs_no_smtp_or_named_environment(tmp_path):
    from tests.test_test_environment import process
    result = process('''import os
os.environ.pop('SMTP_USER',None)
os.environ.pop('SMTP_PASSWORD',None)
from app.main import app
assert app is not None
''', env_file=tmp_path/'development.env', APP_ENV='test', AUTH_MOCK='true',
        DATABASE_URL='sqlite:///'+str(tmp_path/'ordinary.sqlite'))
    assert result.returncode == 0, result.stderr
