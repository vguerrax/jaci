import asyncio
import json
from datetime import timedelta

import httpx
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import select

from app.config import Settings
from tests.helpers.tupa_password_stub import PRODUCT_ID, SERVICE_TOKEN, PasswordProvider


@pytest.fixture
def password_environment(monkeypatch):
    from app.services import access_session_service, password_service, tupa_auth_service

    settings = Settings(
        _env_file=None, app_env="test", auth_mock=False, database_url="sqlite://",
        tupa_url="http://password-provider.test", tupa_product_id=PRODUCT_ID,
        tupa_service_token=SERVICE_TOKEN, session_guard_enabled=True,
        session_token_encryption_key=Fernet.generate_key().decode(),
        password_recovery_min_response_seconds=0,
    )
    for module in (password_service, access_session_service):
        monkeypatch.setattr(module, "get_settings", lambda: settings)
    monkeypatch.setattr(tupa_auth_service, "settings", settings)
    provider = PasswordProvider()
    transport = httpx.MockTransport(lambda request: httpx.Response(**_reply(provider, request)))
    async_client = httpx.AsyncClient
    sync_client = httpx.Client
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: async_client(**kwargs, transport=transport))
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: sync_client(**kwargs, transport=transport))
    tupa_auth_service._jwks.cache_clear()
    yield settings, provider
    tupa_auth_service._jwks.cache_clear()


def _reply(provider, request):
    body = json.loads(request.content) if request.content else {}
    status, value = provider.handle(request.method, request.url.path, request.headers, body)
    return {"status_code": status, "json": value}


@pytest.mark.parametrize("password,confirmation", [
    ("short", "short"), ("x"*129, "x"*129), ("á"*37, "á"*37),
    ("good-password", "different"),
])
def test_password_policy_rejects_invalid_input_without_reflection(password, confirmation):
    from app.services.password_service import PasswordFlowError, validate_password
    with pytest.raises(PasswordFlowError) as error:
        validate_password(password, confirmation)
    assert password not in str(error.value)
    assert confirmation not in str(error.value)


def test_password_wrappers_use_fixed_product_and_required_credentials(password_environment):
    from app.services import tupa_auth_service as tupa
    _, provider = password_environment
    asyncio.run(tupa.forgot_password(" OWNER@EXAMPLE.COM "))
    token = next(iter(provider.reset_tokens))
    asyncio.run(tupa.reset_password(token, "new-password"))
    assert provider.accounts[next(iter(provider.accounts))]["password"] == "new-password"


def test_mock_password_operations_never_call_provider(password_environment):
    from app.services import tupa_auth_service as tupa
    settings, provider = password_environment
    settings.auth_mock = True
    for operation in (
        tupa.forgot_password("owner@example.com"),
        tupa.reset_password("opaque", "new-password"),
        tupa.change_password("access", "old-password", "new-password"),
    ):
        with pytest.raises(tupa.TupaError) as error:
            asyncio.run(operation)
        assert error.value.status_code == 501
    assert provider.calls == []


def test_recovery_limit_is_shared_and_stores_only_hashes(db, password_environment):
    from app.models.auth_rate_limit import AuthRateLimit
    from app.services import password_service

    settings, provider = password_environment
    settings.password_recovery_email_limit = 2
    for _ in range(4):
        asyncio.run(password_service.request_recovery(db, "owner@example.com", "192.0.2.1"))
    assert provider.calls.count("/auth/forgot-password") == 2
    rows = db.scalars(select(AuthRateLimit)).all()
    assert rows and all(len(row.key_hash) == 64 for row in rows)
    assert all("owner" not in row.key_hash and "192.0.2.1" not in row.key_hash for row in rows)


def test_origin_limit_is_generic_429(db, password_environment):
    from app.services import password_service
    settings, _ = password_environment
    settings.password_recovery_origin_limit = 2
    for index in range(2):
        asyncio.run(password_service.request_recovery(db, f"unknown-{index}@example.com", "192.0.2.1"))
    with pytest.raises(password_service.PasswordFlowError) as error:
        asyncio.run(password_service.request_recovery(db, "another@example.com", "192.0.2.1"))
    assert error.value.status_code == 429


def test_reset_context_is_encrypted_product_bound_and_expires(password_environment):
    from app.services.password_service import seal_reset_token, open_reset_token
    from app.services.session_policy import utc_now
    settings, _ = password_environment
    token = "opaque-synthetic-token"
    now = utc_now()
    context = seal_reset_token(token, now=now)
    assert token not in context
    assert open_reset_token(context, now=now) == token
    assert open_reset_token(context+"altered", now=now) is None
    assert open_reset_token(context, now=now+timedelta(hours=1, seconds=1)) is None
    settings.tupa_product_id = "another-product"
    assert open_reset_token(context, now=now) is None


def test_password_urls_are_redacted_from_access_and_client_logs():
    import logging
    from app.utils.password_privacy import PasswordLogFilter
    for message, args in (
        ("%s - %s %s HTTP/%s %s", ("client", "GET", "/reset-password?token=synthetic-secret", "1.1", 303)),
        ('HTTP Request: GET %s "303"', ("http://test/reset-password?token=synthetic-secret",)),
    ):
        record = logging.LogRecord("synthetic", logging.INFO, "", 1, message, args, None)
        assert PasswordLogFilter().filter(record)
        assert "synthetic-secret" not in record.getMessage()
        assert "/reset-password" in record.getMessage()


def test_rate_window_expires_and_old_hashes_are_removed(db, password_environment, monkeypatch):
    from app.models.auth_rate_limit import AuthRateLimit
    from app.services import password_service
    from app.services.session_policy import utc_now

    settings, provider = password_environment
    settings.password_recovery_email_limit = 1
    now = utc_now()
    monkeypatch.setattr(password_service, "utc_now", lambda: now)
    asyncio.run(password_service.request_recovery(db, "owner@example.com", "192.0.2.1"))
    asyncio.run(password_service.request_recovery(db, "owner@example.com", "192.0.2.1"))
    assert provider.calls.count("/auth/forgot-password") == 1
    monkeypatch.setattr(password_service, "utc_now", lambda: now+timedelta(seconds=settings.password_recovery_window_seconds+1))
    asyncio.run(password_service.request_recovery(db, "owner@example.com", "192.0.2.1"))
    assert provider.calls.count("/auth/forgot-password") == 2
    assert len(db.scalars(select(AuthRateLimit)).all()) == 2


def test_existing_sqlite_adoption_adds_auth_metadata_without_losing_users(tmp_path):
    import os
    import subprocess
    import sys
    from sqlalchemy import create_engine, inspect
    from app.database import Base
    from app.models import AccessSession, AuthRateLimit, User

    path = tmp_path/"legacy.sqlite3"
    engine = create_engine("sqlite:///"+str(path))
    Base.metadata.create_all(engine)
    AuthRateLimit.__table__.drop(engine)
    AccessSession.__table__.drop(engine)
    with engine.begin() as connection:
        connection.execute(User.__table__.insert().values(
            email="legacy@example.com", name="Legacy", is_profile_complete=True, is_active=True,
        ))
    engine.dispose()
    result = subprocess.run(
        [sys.executable, "-m", "scripts.apply_migrations"],
        env={**os.environ, "DATABASE_URL":"sqlite:///"+str(path), "DEBUG":"false"},
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    engine = create_engine("sqlite:///"+str(path))
    try:
        assert inspect(engine).has_table("auth_rate_limits")
        assert inspect(engine).has_table("access_sessions")
        with engine.connect() as connection:
            assert connection.scalar(select(User.email)) == "legacy@example.com"
    finally:
        engine.dispose()


def test_uvicorn_access_formatter_preserves_status_and_removes_reset_secret():
    import logging
    from uvicorn.logging import AccessFormatter
    from app.utils.password_privacy import PasswordLogFilter

    record = logging.LogRecord(
        "uvicorn.access", logging.INFO, "", 1, '%s - "%s %s HTTP/%s" %d',
        ("127.0.0.1:1234", "GET", "/reset-password?token=synthetic-secret", "1.1", 303), None,
    )
    PasswordLogFilter().filter(record)
    rendered = AccessFormatter('%(request_line)s %(status_code)s', use_colors=False).format(record)
    assert "synthetic-secret" not in rendered
    assert "303" in rendered
    assert "GET /reset-password?[redacted] HTTP/1.1" in rendered


def test_password_provider_timeout_is_recoverable_without_repeating_operation(password_environment, monkeypatch):
    from app.services import password_service, tupa_auth_service
    _, provider = password_environment
    calls = []

    async def timeout(*args, **kwargs):
        calls.append('reset')
        raise tupa_auth_service.TupaError('private network information', 502)

    monkeypatch.setattr(tupa_auth_service, 'reset_password', timeout)
    context = password_service.seal_reset_token('synthetic-token')
    with pytest.raises(password_service.PasswordFlowError) as error:
        asyncio.run(password_service.reset_password(context, 'new-secret-password', 'new-secret-password'))
    assert error.value.status_code == 503
    assert 'Tente entrar com a nova senha' in str(error.value)
    assert 'private network information' not in str(error.value)
    assert calls == ['reset']
    assert provider.calls == []
