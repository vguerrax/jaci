"""Servidor HTTP sintético usado exclusivamente pelo runner de UI da BL-0010."""
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tests.helpers.tupa_password_stub import PasswordProvider

provider = PasswordProvider(os.environ.get("PLAYWRIGHT_BASE_URL", "http://testserver"))
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/_tests/outbox")
def outbox():
    return provider.outbox


@app.post("/_tests/reset")
def reset():
    provider.reset()
    return {"ok": True}


@app.api_route("/{path:path}", methods=["GET", "POST"])
async def endpoint(path: str, request: Request):
    body = await request.json() if await request.body() else {}
    status, payload = provider.handle(request.method, "/"+path, request.headers, body)
    return JSONResponse(payload, status_code=status)
