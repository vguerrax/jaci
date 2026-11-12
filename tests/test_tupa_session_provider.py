import json
import time
import uuid
from types import SimpleNamespace

import httpx
import pytest
from jose import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from app.services.session_policy import SessionExpired
from app.services.session_provider import ProviderUnavailable, TupaSessionProvider


@pytest.fixture(scope="module")
def signing_key():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


@pytest.fixture
def contract(signing_key, monkeypatch):
    settings = SimpleNamespace(
        tupa_url="http://tupa.example.test", tupa_timeout_seconds=2,
        tupa_product_id=str(uuid.uuid4()), tupa_service_token="synthetic-service-token",
        tupa_jwt_issuer="tupa", auth_mock=False, app_env="test",
    )
    subject = str(uuid.uuid4())
    claims = {
        "iss": "tupa", "sub": subject, "product_id": settings.tupa_product_id,
        "type": "access", "jti": str(uuid.uuid4()),
        "iat": int(time.time()), "exp": int(time.time()) + 900,
    }
    access = jwt.encode(claims, signing_key, algorithm="RS256")
    responses = {
        "/auth/session/validate": (200, {
            "active": True, "sub": subject, "product_id": settings.tupa_product_id,
            "exp": claims["exp"],
        }),
        "/auth/refresh": (200, {
            "access_token": access, "refresh_token": "new-synthetic-refresh",
            "expires_in": 900, "token_type": "bearer",
        }),
        "/auth/logout": (200, {"ok": True, "detail": "Logged out"}),
    }
    requests = []

    def transport(request):
        requests.append(request)
        status, body = responses[request.url.path]
        return httpx.Response(status, json=body)

    client_class = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: client_class(
        **kwargs, transport=httpx.MockTransport(transport),
    ))
    return TupaSessionProvider(settings), claims, access, responses, requests


def test_validation_uses_authenticated_published_contract(contract):
    provider, expected, access, _, requests = contract
    assert provider.validate({"access_token": access}) == expected
    request = requests[0]
    assert request.url.path == "/auth/session/validate"
    assert json.loads(request.content) == {"access_token": access}
    assert request.headers["X-Service-Token"] == "synthetic-service-token"
    assert len(requests) == 1


def test_inactive_response_is_revoked_session(contract):
    provider, _, access, responses, _ = contract
    responses["/auth/session/validate"] = (200, {"active": False})
    with pytest.raises(SessionExpired):
        provider.validate({"access_token": access})


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500, 503])
def test_service_credential_or_provider_failure_does_not_revoke_user(contract, status):
    provider, _, access, responses, _ = contract
    responses["/auth/session/validate"] = (status, {"detail": "synthetic-error"})
    with pytest.raises(ProviderUnavailable):
        provider.validate({"access_token": access})


@pytest.mark.parametrize("field,value", [
    ("active", "true"), ("product_id", "another-product"), ("sub", "another-user"),
    ("exp", 1), ("sub", None),
])
def test_malformed_active_response_never_authorizes(contract, field, value):
    provider, _, access, responses, _ = contract
    responses["/auth/session/validate"][1][field] = value
    with pytest.raises(ProviderUnavailable):
        provider.validate({"access_token": access})


def test_jwt_identity_and_issuer_must_match_the_provider(contract, signing_key):
    provider, claims, _, _, _ = contract
    for change in ({"iss": "another-issuer"}, {"type": "refresh"},
                   {"product_id": str(uuid.uuid4())}):
        invalid = jwt.encode({**claims, **change}, signing_key, algorithm="RS256")
        with pytest.raises(SessionExpired):
            provider.validate({"access_token": invalid})


def test_refresh_uses_existing_rotating_endpoint(contract):
    provider, _, _, _, requests = contract
    result = provider.refresh("synthetic-refresh")
    assert result["refresh_token"] == "new-synthetic-refresh"
    assert requests[0].url.path == "/auth/refresh"
    assert json.loads(requests[0].content) == {"refresh_token": "synthetic-refresh"}


def test_rejected_refresh_expires_session_but_server_failure_preserves_it(contract):
    provider, _, _, responses, _ = contract
    responses["/auth/refresh"] = (401, {"detail": "invalid"})
    with pytest.raises(SessionExpired):
        provider.refresh("synthetic-refresh")
    responses["/auth/refresh"] = (503, {"detail": "unavailable"})
    with pytest.raises(ProviderUnavailable):
        provider.refresh("synthetic-refresh")


def test_logout_sends_bearer_and_accepts_previously_revoked_token(contract):
    provider, _, access, responses, requests = contract
    provider.logout(access)
    assert requests[0].url.path == "/auth/logout"
    assert requests[0].headers["Authorization"] == f"Bearer {access}"
    responses["/auth/logout"] = (401, {"detail": "invalid"})
    provider.logout(access)


def test_missing_configuration_fails_before_network(contract):
    provider, _, access, _, requests = contract
    provider.settings.tupa_service_token = ""
    with pytest.raises(ProviderUnavailable):
        provider.validate({"access_token": access})
    assert requests == []
