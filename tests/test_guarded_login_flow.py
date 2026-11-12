import re
import tempfile
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models.access_session import AccessSession


def test_guarded_login_uses_normal_route_and_logout_revokes_opaque_cookie(
    db, make_user, make_group, tmp_path, monkeypatch,
):
    from app import config, database, main
    from app.routers import auth
    from app.services import access_session_service as sessions, auth_service, session_provider
    from app.services import test_auth_service as mock, tupa_auth_service
    from app.utils import session_http

    settings = Settings(
        _env_file=None, app_env="test", auth_mock=True, session_guard_enabled=True,
        database_url="sqlite://", smtp_user="test@example.com", smtp_password="synthetic",
    )
    for module in (config, sessions, auth_service, session_provider, session_http, mock):
        monkeypatch.setattr(module, "get_settings", lambda: settings)
    for module in (main, auth, tupa_auth_service):
        monkeypatch.setattr(module, "settings", settings)
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
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
    user = make_user("session-entry@example.com")
    make_group(owner=user)
    try:
        with TestClient(main.app) as client:
            page = client.get("/auth/login")
            csrf = re.search(r'name="_csrf" value="([^"]+)"', page.text).group(1)
            result = client.post("/auth/password-login", data={
                "email": user.email, "password": "", "_csrf": csrf, "return_to": "/sync",
            }, follow_redirects=False)
            assert result.status_code == 303 and result.headers["location"] == "/sync"
            reference = client.cookies.get("jaci_session")
            assert len(reference) == 43 and "." not in reference
            assert client.cookies.get("jaci_refresh") is None

            page = client.get("/sync")
            assert page.status_code == 200 and 'name="jwt-token"' not in page.text
            owner = re.search(r'name="jaci-offline-owner" content="([^"]+)"', page.text).group(1)
            assert client.get("/api/offline/snapshot", headers={
                "X-Jaci-Offline-Owner": owner,
            }).status_code == 200
            assert client.post("/auth/profile", data={
                "_csrf": "forged", "name": "changed", "email": user.email,
            }).status_code == 403
            confirmation = client.get("/auth/logout")
            csrf = re.search(r'name="_csrf" value="([^"]+)"', confirmation.text).group(1)
            logout = client.post("/auth/logout", data={"_csrf": csrf}, follow_redirects=False)
            assert logout.status_code == 303
            assert client.cookies.get("jaci_session") is None
            assert client.get("/sync", follow_redirects=False).status_code == 303
        db.expire_all()
        assert db.scalar(select(AccessSession)).revoked_at is not None
        assert db.get(type(user), user.id).name != "changed"
    finally:
        main.app.dependency_overrides.pop(database.get_db, None)


def test_first_access_and_expiration_have_distinct_login_messages(monkeypatch):
    from urllib.parse import parse_qs, urlsplit

    from app import main
    from app.services.session_policy import SessionExpired
    from app.utils import session_http

    settings = Settings(
        _env_file=None, app_env="test", session_guard_enabled=True, database_url="sqlite://",
        smtp_user="synthetic@example.com", smtp_password="synthetic",
    )
    monkeypatch.setattr(session_http, "get_settings", lambda: settings)

    def expired(_reference, touch=True):
        raise SessionExpired()

    monkeypatch.setattr(session_http, "_load", expired)
    cases = [
        ({}, False),
        ({"jaci_login_csrf": "anonymous-form"}, False),
        ({"jaci_session": "expired-reference"}, True),
        ({"jaci_offline_owner": "a" * 64}, True),
    ]
    for cookies, should_warn in cases:
        with TestClient(main.app) as client:
            client.cookies.update(cookies)
            redirect = client.get("/", follow_redirects=False)
            assert redirect.status_code == 303
            target = redirect.headers["location"]
            query = parse_qs(urlsplit(target).query)
            assert query["return_to"] == ["/"]
            assert ("expired" in query) is should_warn
            page = client.get(target)
            assert page.status_code == 200
            assert ("Sua sessão terminou." in page.text) is should_warn

            response = client.get("/api/offline/snapshot")
            assert response.status_code == 401
            expected = "session_expired" if should_warn else "authentication_required"
            assert response.json()["detail"]["code"] == expected
            assert ("expired" in parse_qs(urlsplit(response.headers["X-Session-Login"]).query)) is should_warn
