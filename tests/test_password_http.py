import asyncio
import re
from contextlib import contextmanager
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from tests.helpers.tupa_password_stub import INITIAL_PASSWORD, OWNER_SUBJECT
from tests.test_password_recovery import password_environment


@pytest.fixture
def password_client(db, make_user, make_group, password_environment, monkeypatch):
    from app import config, database, main
    from app.routers import auth, passwords
    from app.services import auth_service, session_provider
    from app.utils import session_http

    settings, provider = password_environment
    for module in (config, auth_service, session_provider, session_http, passwords):
        monkeypatch.setattr(module, "get_settings", lambda: settings)
    for module in (main, auth):
        monkeypatch.setattr(module, "settings", settings)
    monkeypatch.setattr(database, "SessionLocal", lambda: Session(db.get_bind()))
    monkeypatch.setattr(main, "SessionLocal", lambda: Session(db.get_bind()))

    @contextmanager
    def session_database():
        with Session(db.get_bind()) as connection:
            yield connection

    def request_database():
        with Session(db.get_bind()) as connection:
            yield connection

    monkeypatch.setattr(session_http, "session_database", session_database)
    main.app.dependency_overrides[database.get_db] = request_database
    user = make_user("owner@example.com")
    user.tupa_user_id = OWNER_SUBJECT
    db.commit()
    make_group(owner=user)
    try:
        with TestClient(main.app) as client:
            yield client, provider, user, settings
    finally:
        main.app.dependency_overrides.pop(database.get_db, None)


def csrf(page):
    return re.search(r'name="_csrf" value="([^"]+)"', page.text).group(1)


def login(client, password=INITIAL_PASSWORD):
    page = client.get("/auth/login")
    return client.post("/auth/password-login", data={
        "email": "owner@example.com", "password": password, "_csrf": csrf(page),
    }, follow_redirects=False)


def request_link(client, provider):
    page = client.get("/auth/forgot-password")
    response = client.post("/auth/forgot-password", data={
        "email": "owner@example.com", "_csrf": csrf(page),
    })
    assert response.status_code == 200
    return provider.outbox[-1]["url"]


def test_recovery_confirmation_is_generic_and_scanner_does_not_consume_token(password_client, db):
    client, provider, _, _ = password_client
    responses = []
    for email in ("owner@example.com", "unknown@example.com"):
        page = client.get("/auth/forgot-password")
        responses.append(client.post("/auth/forgot-password", data={"email": email, "_csrf": csrf(page)}))
    assert responses[0].status_code == responses[1].status_code == 200
    assert responses[0].text == responses[1].text
    link = provider.outbox[-1]["url"]
    reset = client.get(link, follow_redirects=False)
    assert reset.status_code == 303
    assert reset.headers["location"] == "/auth/reset-password"
    assert reset.headers["cache-control"] == "no-store"
    assert reset.headers["referrer-policy"] == "no-referrer"
    token = parse_qs(urlsplit(link).query)["token"][0]
    clean = client.get(reset.headers["location"])
    assert clean.status_code == 200 and token not in clean.text
    assert not provider.reset_tokens[token]["used"]
    assert "/auth/reset-password" not in provider.calls
    assert db.scalars(select(User)).all()[0].email == "owner@example.com"


def test_reset_changes_password_and_ends_existing_sessions_without_auto_login(password_client, db):
    from app.services import access_session_service as sessions, tupa_auth_service
    from app.services.session_policy import SessionExpired

    client, provider, user, _ = password_client
    other = sessions.issue_session(db, user, asyncio.run(tupa_auth_service.token(user.email, INITIAL_PASSWORD)))
    link = request_link(client, provider)
    client.get(link)
    page = client.get("/auth/reset-password")
    body = {"new_password": "new-secret-password", "new_password_confirm": "new-secret-password", "_csrf": csrf(page)}
    response = client.post("/auth/reset-password", data=body, follow_redirects=False)
    assert response.status_code == 303 and "/auth/login" in response.headers["location"]
    assert client.cookies.get("jaci_session") is None
    assert "new-secret-password" not in response.text
    with pytest.raises(SessionExpired):
        sessions.load_session(db, other.session_id)
    assert login(client).status_code == 400
    assert login(client, "new-secret-password").status_code == 303


def test_invalid_reset_and_foreign_product_never_change_password(password_client):
    client, provider, _, _ = password_client
    link = request_link(client, provider)
    token = parse_qs(urlsplit(link).query)["token"][0]
    provider.reset_tokens[token]["used"] = True
    client.get(link)
    page = client.get("/auth/reset-password")
    response = client.post("/auth/reset-password", data={
        "new_password": "new-secret-password", "new_password_confirm": "new-secret-password", "_csrf": csrf(page),
    })
    assert response.status_code == 400
    assert "Link inválido ou expirado" in response.text
    assert token not in response.text and "new-secret-password" not in response.text
    assert login(client).status_code == 303


def test_profile_uses_session_identity_and_wrong_current_password_preserves_session(password_client):
    client, provider, _, _ = password_client
    assert login(client).status_code == 303
    page = client.get("/auth/profile")
    response = client.post("/auth/profile/password", data={
        "_csrf": csrf(page), "current_password": "incorrect", "new_password": "new-secret-password",
        "new_password_confirm": "new-secret-password", "user_id": "foreign-user",
    })
    assert response.status_code == 400
    assert "A senha atual está incorreta" in response.text
    assert client.get("/auth/profile").status_code == 200
    page = client.get("/auth/profile")
    response = client.post("/auth/profile/password", data={
        "_csrf": csrf(page), "current_password": INITIAL_PASSWORD,
        "new_password": "new-secret-password", "new_password_confirm": "new-secret-password",
        "user_id": "foreign-user",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert client.cookies.get("jaci_session") is None
    assert login(client, "new-secret-password").status_code == 303


def test_reset_requires_csrf_and_never_reflects_password_or_token(password_client):
    client, provider, _, _ = password_client
    link = request_link(client, provider)
    client.get(link)
    response = client.post("/auth/reset-password", data={
        "new_password": "secret-password", "new_password_confirm": "secret-password",
    })
    assert response.status_code == 403
    assert "secret-password" not in response.text
    assert not any(entry["used"] for entry in provider.reset_tokens.values())


def test_context_supports_maximum_token_without_exposing_it(password_client):
    client, _, _, _ = password_client
    token = "x" * 4096
    response = client.get("/reset-password", params={"token": token}, follow_redirects=False)
    assert response.status_code == 303
    headers = response.headers.get_list("set-cookie")
    assert all(len(value) < 4096 for value in headers)
    assert token not in response.text
    page = client.get("/auth/reset-password")
    assert page.status_code == 200
    assert 'name="new_password"' in page.text
    assert token not in page.text


def test_mock_exposes_unavailable_password_operation_without_network(password_client):
    client, provider, _, settings = password_client
    settings.auth_mock = True
    page = client.get("/auth/forgot-password")
    response = client.post("/auth/forgot-password", data={"email": "owner@example.com", "_csrf": csrf(page)})
    assert response.status_code == 501
    assert provider.calls == []


def test_no_referrer_form_accepts_null_origin_only_with_signed_csrf(password_client):
    client, provider, _, _ = password_client
    page = client.get("/auth/forgot-password")
    response = client.post("/auth/forgot-password", headers={"Origin": "null"}, data={
        "email": "owner@example.com", "_csrf": csrf(page),
    })
    assert response.status_code == 200
    assert provider.outbox
    before = len(provider.calls)
    client.cookies.clear()
    client.cookies.set("jaci_login_csrf", "attacker-chosen")
    response = client.post("/auth/forgot-password", headers={"Origin": "null"}, data={
        "email": "owner@example.com", "_csrf": "attacker-chosen",
    })
    assert response.status_code == 403
    assert len(provider.calls) == before


def test_foreign_origin_is_refused_even_with_correct_form_token(password_client):
    client, provider, _, _ = password_client
    page = client.get("/auth/forgot-password")
    response = client.post("/auth/forgot-password", headers={"Origin": "https://foreign.example"}, data={
        "email": "owner@example.com", "_csrf": csrf(page),
    })
    assert response.status_code == 403
    assert provider.calls == []


def test_foreign_product_reset_is_refused_by_the_provider(password_client):
    client, provider, _, _ = password_client
    provider.accounts["foreign-subject"] = {
        "email":"foreign@example.com", "password":"foreign-password",
        "product_id":"00000000-0000-0000-0000-000000000999", "generation":0,
    }
    provider.reset_tokens["foreign-reset"] = {"subject":"foreign-subject", "used":False, "expires":float("inf")}
    client.get("/reset-password", params={"token":"foreign-reset"})
    page = client.get("/auth/reset-password")
    response = client.post("/auth/reset-password", data={
        "_csrf":csrf(page), "new_password":"new-secret-password",
        "new_password_confirm":"new-secret-password",
    })
    assert response.status_code == 400
    assert provider.accounts["foreign-subject"]["password"] == "foreign-password"
    assert provider.reset_tokens["foreign-reset"]["used"] is False


def test_provider_failure_is_generic_and_never_reflects_remote_secrets(password_client, monkeypatch):
    client, provider, _, _ = password_client
    original = provider.handle

    def unavailable(method, path, headers, body):
        if path == "/auth/forgot-password":
            return 503, {"detail":"private-provider-secret"}
        return original(method, path, headers, body)

    monkeypatch.setattr(provider, "handle", unavailable)
    page = client.get("/auth/forgot-password")
    response = client.post("/auth/forgot-password", data={
        "email":"owner@example.com", "_csrf":csrf(page),
    })
    assert response.status_code == 503
    assert "private-provider-secret" not in response.text
    assert "Tente novamente mais tarde." in response.text


def test_password_change_revoked_bearer_is_not_reported_as_wrong_password(password_client, monkeypatch):
    from app.services import tupa_auth_service as tupa
    client, provider, _, _ = password_client
    login(client)
    page = client.get('/auth/profile')

    async def concurrent_revocation(*args):
        provider.accounts[OWNER_SUBJECT]['generation'] += 1
        raise tupa.TupaError('private provider detail', 401)

    monkeypatch.setattr(tupa, 'change_password', concurrent_revocation)
    response = client.post('/auth/profile/password', data={
        '_csrf':csrf(page), 'current_password':INITIAL_PASSWORD,
        'new_password':'new-secret-password', 'new_password_confirm':'new-secret-password',
    })
    assert response.status_code == 401
    assert response.json()['detail']['code'] == 'session_revoked'
    assert 'senha atual está incorreta' not in response.text
    assert provider.accounts[OWNER_SUBJECT]['password'] == INITIAL_PASSWORD


def test_password_change_success_survives_local_cleanup_failure(password_client, monkeypatch):
    from sqlalchemy.exc import OperationalError
    from app.services import access_session_service as sessions
    client, provider, _, _ = password_client
    login(client)
    page = client.get('/auth/profile')

    def unavailable(*args):
        raise OperationalError('synthetic cleanup failure', {}, Exception('unavailable'))

    monkeypatch.setattr(sessions, 'revoke_user_sessions', unavailable)
    response = client.post('/auth/profile/password', data={
        '_csrf':csrf(page), 'current_password':INITIAL_PASSWORD,
        'new_password':'new-secret-password', 'new_password_confirm':'new-secret-password',
    }, follow_redirects=False)
    assert response.status_code == 303
    assert client.cookies.get('jaci_session') is None
    assert provider.accounts[OWNER_SUBJECT]['password'] == 'new-secret-password'
    assert login(client, 'new-secret-password').status_code == 303
