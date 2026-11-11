"""BL-0019: persistência, rotação e HTTP. Não executar sem liberação."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from cryptography.fernet import Fernet
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.access_session import AccessSession
from app.services import access_session_service as sessions
from app.services.session_policy import SessionExpired, SessionUnavailable
from app.services.session_provider import ProviderUnavailable
from app.utils.session_http import SessionMiddleware

NOW = datetime(2026, 11, 10, tzinfo=timezone.utc)


class Provider:
    name = 'tupa'
    def __init__(self, subject):
        self.subject = subject
        self.rotations = 0
        self.active = True
        self.unavailable = False
    def validate(self, tokens):
        if self.unavailable:
            raise ProviderUnavailable()
        if not self.active:
            raise SessionExpired('session_revoked')
        return {'sub': str(self.subject), 'product_id': 'synthetic-product', 'type': 'access'}
    def refresh(self, refresh):
        self.rotations += 1
        return {'access_token': f'access-{self.rotations}', 'refresh_token': f'refresh-{self.rotations}',
                'expires_in': 900, 'token_type': 'bearer'}
    def logout(self, token):
        self.active = False


@pytest.fixture
def guard(db, make_user, monkeypatch):
    user = make_user('guard@example.test')
    user.tupa_user_id = 'synthetic-subject'
    db.commit()
    settings = SimpleNamespace(session_guard_enabled=True, auth_mock=False, app_env='test',
                               session_token_encryption_key=Fernet.generate_key().decode(),
                               tupa_product_id='synthetic-product', secure_cookie=False,
                               jwt_secret_key='synthetic-csrf-secret', app_url='http://testserver')
    provider = Provider(user.tupa_user_id)
    monkeypatch.setattr(sessions, 'get_settings', lambda: settings)
    monkeypatch.setattr(sessions, 'provider_for', lambda _: provider)
    monkeypatch.setattr(sessions, 'utc_now', lambda: NOW)
    return user, settings, provider


def issue(db, guard):
    user, _, provider = guard
    return sessions.issue_session(db, user, provider.refresh('initial'), now=NOW)


def test_cookie_reference_is_random_and_tokens_are_not_persisted_open(db, guard):
    grant = issue(db, guard)
    row = db.scalar(select(AccessSession))
    assert row.id_hash != grant.session_id and len(grant.session_id) >= 43
    assert 'access-' not in row.encrypted_tokens and 'refresh-' not in row.encrypted_tokens
    assert grant.expires_at == NOW + timedelta(hours=8)


def test_each_request_touches_even_automatic_and_under_one_minute(db, guard):
    grant = issue(db, guard)
    first = sessions.load_session(db, grant.session_id, now=NOW+timedelta(seconds=1))
    second = sessions.load_session(db, grant.session_id, now=NOW+timedelta(seconds=2))
    assert second.expires_at > first.expires_at
    assert guard[2].rotations == 1


def test_expired_local_session_never_refreshes_or_resurrects(db, guard):
    grant = issue(db, guard)
    with pytest.raises(SessionExpired):
        sessions.load_session(db, grant.session_id, now=NOW+timedelta(hours=8))
    assert guard[2].rotations == 1


def test_refresh_only_after_access_expiry_and_ping_does_not_touch(db, guard):
    grant = issue(db, guard)
    now = NOW + timedelta(minutes=16)
    sessions.load_session(db, grant.session_id, touch=True, now=now)
    assert guard[2].rotations == 2
    before = db.scalar(select(AccessSession)).last_activity_at
    sessions.load_session(db, grant.session_id, touch=False, now=now+timedelta(seconds=10))
    assert db.scalar(select(AccessSession)).last_activity_at == before


def test_unavailable_provider_does_not_extend_or_revoke(db, guard):
    grant = issue(db, guard)
    guard[2].unavailable = True
    with pytest.raises(SessionUnavailable):
        sessions.load_session(db, grant.session_id, now=NOW+timedelta(seconds=1))
    row = db.scalar(select(AccessSession))
    assert row.revoked_at is None
    assert sessions.as_utc(row.last_activity_at) == NOW


def test_revoked_provider_denies_still_unexpired_access(db, guard):
    grant = issue(db, guard)
    guard[2].active = False
    with pytest.raises(SessionExpired):
        sessions.load_session(db, grant.session_id, now=NOW+timedelta(seconds=1))


def test_logout_all_local_sessions_and_inactive_user(db, guard):
    first = issue(db, guard)
    second = issue(db, guard)
    sessions.revoke_user_sessions(db, guard[0].id)
    for grant in (first, second):
        with pytest.raises(SessionExpired):
            sessions.load_session(db, grant.session_id)


def test_legacy_jwt_cannot_bootstrap_guard_session(db, guard):
    with pytest.raises(SessionExpired):
        sessions.load_session(db, 'eyJ.jwt.raw')
    assert db.scalar(select(AccessSession)) is None


def test_real_adapter_requires_configuration_before_network(monkeypatch):
    from app.services.session_provider import TupaSessionProvider
    monkeypatch.setattr('httpx.Client', lambda *_args, **_kwargs: pytest.fail('invented remote API'))
    with pytest.raises(ProviderUnavailable):
        TupaSessionProvider(guard_settings=None).validate({'access_token':'synthetic'})


def test_idle_is_rechecked_after_slow_refresh(db, guard, monkeypatch):
    grant = issue(db, guard)
    row = db.scalar(select(AccessSession))
    row.access_expires_at = NOW
    db.commit()
    clock = iter([NOW+timedelta(hours=7, minutes=59), NOW+timedelta(hours=8)])
    monkeypatch.setattr(sessions, 'utc_now', lambda: next(clock))
    with pytest.raises(SessionExpired):
        sessions.load_session(db, grant.session_id)


def test_http_background_counts_but_expired_post_never_reaches_handler(db, guard, monkeypatch):
    from contextlib import contextmanager
    from app.utils import session_http
    @contextmanager
    def factory():
        yield db
    monkeypatch.setattr(session_http, 'get_settings', lambda: guard[1])
    monkeypatch.setattr(session_http, 'utc_now', lambda: NOW)
    monkeypatch.setattr(session_http, 'session_database', factory)
    app = FastAPI()
    app.add_middleware(SessionMiddleware)
    writes = []
    @app.get('/snapshot')
    def snapshot(request: Request):
        return {'user': request.state.auth_session.user_id}
    @app.post('/write')
    def write():
        writes.append(1)
        return {'ok': True}
    grant = issue(db, guard)
    with TestClient(app) as client:
        client.cookies.set('jaci_session', grant.session_id)
        assert client.get('/snapshot').status_code == 200
        monkeypatch.setattr(sessions, 'utc_now', lambda: NOW+timedelta(hours=8))
        assert client.post('/write', headers={'Accept':'application/json'}).status_code == 401
    assert writes == []


def test_offline_requests_require_matching_owner_and_csrf(db, guard, monkeypatch):
    from contextlib import contextmanager
    from app.utils import session_http

    @contextmanager
    def factory():
        yield db

    monkeypatch.setattr(session_http, 'get_settings', lambda: guard[1])
    monkeypatch.setattr(session_http, 'utc_now', lambda: NOW)
    monkeypatch.setattr(session_http, 'session_database', factory)
    app = FastAPI()
    app.add_middleware(SessionMiddleware)

    @app.post('/api/offline/operations/write')
    def write():
        return {'applied': True}

    grant = issue(db, guard)
    with TestClient(app) as client:
        client.cookies.set('jaci_session', grant.session_id)
        url = '/api/offline/operations/write'
        stale = client.post(url, headers={'X-Jaci-Offline-Owner': 'old-account'})
        assert stale.status_code == 403
        assert stale.json()['detail']['code'] == 'offline_account_changed'
        assert client.post(url, headers={'X-Jaci-Offline-Owner': grant.owner}).status_code == 403
        response = client.post(url, headers={
            'X-Jaci-Offline-Owner': grant.owner,
            'X-CSRF-Token': grant.csrf_token,
        })
        assert response.json() == {'applied': True}


def test_access_expiring_during_validation_refreshes_once_without_ending_session(db, guard, monkeypatch):
    from app.services.session_policy import AccessTokenExpired

    grant = issue(db, guard)
    original = guard[2].validate
    calls = []

    def validate(tokens):
        calls.append(tokens["access_token"])
        if len(calls) == 1:
            raise AccessTokenExpired()
        return original(tokens)

    monkeypatch.setattr(guard[2], "validate", validate)
    renewed = sessions.load_session(db, grant.session_id, now=NOW + timedelta(seconds=1))
    assert renewed.session_id == grant.session_id
    assert guard[2].rotations == 2
    assert db.scalar(select(AccessSession)).revoked_at is None


def test_websocket_expired_access_waits_for_http_without_rotating_or_revoking(db, guard, monkeypatch):
    from app.services.session_policy import AccessTokenExpired

    grant = issue(db, guard)

    def expired(_tokens):
        raise AccessTokenExpired()

    monkeypatch.setattr(guard[2], "validate", expired)
    with pytest.raises(SessionExpired, match="Autenticação"):
        sessions.load_session(db, grant.session_id, touch=False, allow_refresh=False)
    assert guard[2].rotations == 1
    assert db.scalar(select(AccessSession)).revoked_at is None
