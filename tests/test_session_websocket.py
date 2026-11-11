"""BL-0019: contratos de entrega privada WS, sem execução nesta entrega."""
import asyncio

from app.websocket.manager import ConnectionManager


def test_broadcast_rechecks_each_recipient_without_touching_activity():
    class Socket:
        def __init__(self, active): self.active=active; self.sent=[]; self.closed=[]
        async def accept(self): pass
        async def send_text(self, text): self.sent.append(text)
        async def close(self, **kwargs): self.closed.append(kwargs)
    async def scenario():
        manager=ConnectionManager()
        active, expired=Socket(True),Socket(False)
        async def check(socket): return socket.active
        await manager.connect(active, 1, authorize=lambda:check(active))
        await manager.connect(expired, 1, authorize=lambda:check(expired))
        await manager.broadcast(1,'item_updated',{'item_id':1})
        assert active.sent and not expired.sent
        assert expired.closed[0]['code']==4001
    asyncio.run(scenario())


def test_guarded_handshake_uses_cookie_and_ping_never_touches_activity(monkeypatch):
    from datetime import timedelta
    from types import SimpleNamespace

    import pytest
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from starlette.websockets import WebSocketDisconnect

    from app.services.session_policy import SessionExpired, utc_now
    from app.utils import session_http
    from app.websocket import handlers

    settings = SimpleNamespace(
        session_guard_enabled=True, app_env="test", secure_cookie=False,
        app_url="http://testserver",
    )
    monkeypatch.setattr(session_http, "get_settings", lambda: settings)
    monkeypatch.setattr(handlers, "get_settings", lambda: settings)
    manager = ConnectionManager()
    monkeypatch.setattr(handlers, "manager", manager)
    calls = []
    state = {"active": True}
    reference = "a" * 43

    def identity(cookie, owner, execution_id, *, handshake=False):
        calls.append(handshake)
        assert cookie == reference and owner == "test-owner" and execution_id == 7
        if not state["active"]:
            raise SessionExpired()
        return SimpleNamespace(session_id=reference, expires_at=utc_now()+timedelta(hours=8)), 1, "synthetic@example.com"

    monkeypatch.setattr(handlers, "_guarded_identity", identity)
    app = FastAPI()
    app.websocket("/ws/executions/{execution_id}")(handlers.execution_ws_handler)
    with TestClient(app) as client:
        with client.websocket_connect(
            "/ws/executions/7?owner=test-owner&token=ignored-legacy-token",
            headers={"origin": "http://testserver", "cookie": f"jaci_session={reference}"},
        ) as socket:
            socket.send_json({"event": "ping"})
            assert socket.receive_json() == {"event": "pong", "data": {}}
            assert calls == [True, False]
            state["active"] = False
            socket.send_json({"event": "ping"})
            with pytest.raises(WebSocketDisconnect) as closed:
                socket.receive_json()
            assert closed.value.code == 4001
            assert calls == [True, False, False]
    assert manager._rooms == {}


def test_guarded_websocket_refuses_foreign_origin_before_loading_session(monkeypatch):
    from types import SimpleNamespace

    import pytest
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from starlette.websockets import WebSocketDisconnect

    from app.utils import session_http
    from app.websocket import handlers

    settings = SimpleNamespace(session_guard_enabled=True, app_url="http://testserver")
    monkeypatch.setattr(session_http, "get_settings", lambda: settings)
    monkeypatch.setattr(handlers, "get_settings", lambda: settings)

    def unexpected(*args, **kwargs):
        raise AssertionError("Origem recusada antes de carregar sessão.")

    monkeypatch.setattr(handlers, "_guarded_identity", unexpected)
    app = FastAPI()
    app.websocket("/ws/executions/{execution_id}")(handlers.execution_ws_handler)
    with TestClient(app) as client:
        with pytest.raises(WebSocketDisconnect) as closed:
            with client.websocket_connect("/ws/executions/7", headers={"origin": "https://foreign.example"}):
                pass
        assert closed.value.code == 4003
