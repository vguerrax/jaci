"""Provedor de senha sintético para contratos HTTP e Chromium isolado."""
import secrets
import time
import uuid

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jose import JWTError, jwt

PRODUCT_ID = "00000000-0000-0000-0000-000000000150"
SERVICE_TOKEN = "synthetic-password-service"
OWNER_SUBJECT = str(uuid.uuid5(uuid.NAMESPACE_URL, "jaci-password-owner"))
INITIAL_PASSWORD = "jaci-test-only"
PRIVATE = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PRIVATE_PEM = PRIVATE.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
)
PUBLIC_PEM = PRIVATE.public_key().public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo,
)


class PasswordProvider:
    def __init__(self, base_url="http://testserver"):
        self.base_url = base_url
        self.reset()

    def reset(self):
        self.epoch = getattr(self, "epoch", -1) + 1
        self.accounts = {
            OWNER_SUBJECT: {"email": "owner@example.com", "password": INITIAL_PASSWORD,
                            "product_id": PRODUCT_ID, "generation": self.epoch},
        }
        self.refresh_tokens = {}
        self.reset_tokens = {}
        self.outbox = []
        self.calls = []

    def tokens(self, subject):
        account = self.accounts[subject]
        now = int(time.time())
        access = jwt.encode({
            "sub": subject, "product_id": account["product_id"], "type": "access",
            "iss": "tupa", "iat": now, "exp": now+900, "jti": str(uuid.uuid4()),
            "session_version": account["generation"],
        }, PRIVATE_PEM, algorithm="RS256", headers={"kid": "password-test"})
        refresh = secrets.token_urlsafe(32)
        self.refresh_tokens[refresh] = (subject, account["generation"])
        return {"access_token": access, "refresh_token": refresh,
                "expires_in": 900, "token_type": "bearer"}

    def access(self, token):
        try:
            claims = jwt.decode(token, PUBLIC_PEM, algorithms=["RS256"], issuer="tupa")
            account = self.accounts[claims["sub"]]
            if (claims["type"] != "access"
                    or claims["session_version"] != account["generation"]):
                return None
            return claims
        except (JWTError, KeyError, TypeError):
            return None

    def handle(self, method, path, headers, body):
        self.calls.append(path)
        bearer = headers.get("authorization", "").removeprefix("Bearer ")
        credential = headers.get("x-service-token")
        if path in {"/.well-known/jwks", "/.well-known/jwks.json"}:
            numbers = PRIVATE.public_key().public_numbers()
            from jose.utils import base64url_encode
            def number(value):
                return base64url_encode(value.to_bytes((value.bit_length()+7)//8, "big")).decode()
            return 200, {"keys": [{"kty": "RSA", "alg": "RS256", "kid": "password-test",
                                   "n": number(numbers.n), "e": number(numbers.e)}]}
        if path == "/auth/token":
            for subject, account in self.accounts.items():
                if (account["email"] == body.get("email")
                        and account["product_id"] == body.get("product_id")
                        and account["password"] == body.get("password")):
                    return 200, self.tokens(subject)
            return 401, {"detail": "Invalid credentials"}
        if path == "/auth/refresh":
            entry = self.refresh_tokens.pop(body.get("refresh_token"), None)
            if entry and self.accounts[entry[0]]["generation"] == entry[1]:
                return 200, self.tokens(entry[0])
            return 401, {"detail": "Invalid refresh token"}
        if path == "/auth/session/validate":
            if credential != SERVICE_TOKEN:
                return 401, {"detail": "Unauthorized"}
            claims = self.access(body.get("access_token"))
            if not claims or claims["product_id"] != PRODUCT_ID:
                return 200, {"active": False}
            return 200, {"active": True, **{k: claims[k] for k in ("sub", "product_id", "exp")}}
        if path == "/auth/forgot-password":
            for subject, account in self.accounts.items():
                if account["email"] == body.get("email") and account["product_id"] == body.get("product_id"):
                    token = secrets.token_urlsafe(32)
                    self.reset_tokens[token] = {"subject": subject, "used": False, "expires": time.time()+3600}
                    self.outbox.append({"email": account["email"], "url": self.base_url+"/reset-password?token="+token})
            return 200, {"detail": "Password reset email sent"}
        if path == "/auth/reset-password":
            entry = self.reset_tokens.get(body.get("token"))
            if credential != SERVICE_TOKEN:
                return 401, {"detail": "Unauthorized"}
            if (not entry or entry["used"] or entry["expires"] <= time.time()
                    or self.accounts[entry["subject"]]["product_id"] != PRODUCT_ID):
                return 400, {"detail": "Invalid reset token"}
            account = self.accounts[entry["subject"]]
            account["password"] = body["new_password"]
            account["generation"] += 1
            entry["used"] = True
            return 200, {"detail": "Password changed"}
        if path in {"/auth/change-password", "/auth/logout"}:
            claims = self.access(bearer)
            if not claims:
                return 401, {"detail": "Invalid access token"}
            account = self.accounts[claims["sub"]]
            if path.endswith("change-password"):
                if account["password"] != body.get("current_password"):
                    return 401, {"detail": "Invalid current password"}
                account["password"] = body["new_password"]
            account["generation"] += 1
            return 200, {"detail": "Password changed" if path.endswith("change-password") else "Logged out"}
        return 404, {"detail": "Not found"}
