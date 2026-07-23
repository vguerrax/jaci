import asyncio

from starlette.requests import Request

from app.routers import auth


def make_request(path: str) -> Request:
    return Request({"type": "http", "method": "GET", "path": path})


def test_login_page_only_contains_login_form_and_registration_link():
    response = asyncio.run(auth.login_page(make_request("/auth/login")))
    body = response.body.decode()

    assert 'action="/auth/password-login"' in body
    assert 'href="/auth/register"' in body
    assert "Não possui conta?" in body
    assert 'action="/auth/register"' not in body
    assert 'id="sync-status"' in body
    assert 'id="offline-cache-panel"' not in body


def test_register_page_contains_registration_form_and_login_link():
    response = asyncio.run(auth.register_page(make_request("/auth/register")))
    body = response.body.decode()

    assert 'action="/auth/register"' in body
    assert 'href="/auth/login"' in body
    assert "Já possui conta?" in body
    assert 'action="/auth/password-login"' not in body


def test_invalid_registration_renders_register_page_and_preserves_identity_fields(db):
    response = asyncio.run(
        auth.register(
            request=make_request("/auth/register"),
            name="Ana",
            email="ana@example.com",
            password="curta",
            password_confirm="curta",
            db=db,
        )
    )
    body = response.body.decode()

    assert response.status_code == 400
    assert "A senha deve ter pelo menos 8 caracteres." in body
    assert 'value="Ana"' in body
    assert 'value="ana@example.com"' in body
    assert "Já possui conta?" in body
