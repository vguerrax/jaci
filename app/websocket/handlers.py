import logging
from urllib.parse import urlsplit

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from sqlalchemy import select

from app.database import SessionLocal
from app.websocket.manager import manager
from app.models.user import User
from app.services.execution_service import get_execution_by_id

from app.config import get_settings
from app.services.access_session_service import cookie_grant, load_session
from app.services.session_policy import SessionExpired, SessionUnavailable
from app.utils.session_http import guard_enabled, set_session_cookie

logger = logging.getLogger("jaci.ws")


async def execution_ws_handler(
    websocket: WebSocket,
    execution_id: int,
    token: str | None = None,
):
    """
    Gerencia a conexão WebSocket para uma execução específica.
    Usa cookie opaco quando a sessão persistida está habilitada.
    """
    if guard_enabled():
        await _guarded_connection(websocket, execution_id)
        return

    # Autentica o usuário
    db = SessionLocal()
    user = None
    try:
        if token:
            from app.utils.security import decode_access_token

            payload = decode_access_token(token)
            if payload:
                tupa_user_id = payload.get("sub")
                if tupa_user_id:
                    user = db.scalar(
                        select(User).where(User.tupa_user_id == str(tupa_user_id))
                    )
    except Exception:
        pass
    finally:
        db.close()

    if not user:
        await websocket.close(code=4001, reason="Não autenticado")
        return

    # Verifica acesso à execução
    db = SessionLocal()
    try:
        execution = get_execution_by_id(db, execution_id, user)
        if not execution:
            await websocket.close(code=4003, reason="Acesso negado")
            return
    finally:
        db.close()

    # Conecta à sala
    await manager.connect(websocket, execution_id)

    try:
        while True:
            # Aguarda mensagens do cliente
            data = await websocket.receive_json()

            event = data.get("event")

            if event == "ping":
                await manager.send_personal(websocket, "pong", {})

            elif event == "typing":
                # Usuário está interagindo (placeholder para futuras features)
                await manager.broadcast(
                    execution_id,
                    "user_active",
                    {"user_id": user.id, "email": user.email},
                    exclude=websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, execution_id)
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        manager.disconnect(websocket, execution_id)

def _guarded_identity(reference, owner, execution_id, *, handshake=False):
    with SessionLocal() as db:
        grant = load_session(db, reference, touch=handshake, allow_refresh=handshake)
        user = db.get(User, grant.user_id)
        if (owner != grant.owner or not user or not user.is_active
                or not get_execution_by_id(db, execution_id, user)):
            return None
        user_id, email = user.id, user.email
        if handshake:
            # Usar uma nova transação para revalidar o cookie após checar o grupo.
            db.rollback()
            grant = cookie_grant(db, reference)
            if grant is None:
                raise SessionExpired()
        return grant, user_id, email


def _valid_origin(websocket):
    try:
        origin = urlsplit(websocket.headers.get("origin", ""))
        configured = urlsplit(get_settings().app_url)
        expected_scheme = "https" if websocket.url.scheme == "wss" else "http"
        return bool(origin.netloc) and (origin.scheme, origin.netloc) in {
            (expected_scheme, websocket.url.netloc),
            (configured.scheme, configured.netloc),
        }
    except ValueError:
        return False


async def _guarded_connection(websocket, execution_id):
    if not _valid_origin(websocket):
        await websocket.close(code=4003)
        return
    reference = websocket.cookies.get("jaci_session")
    owner = websocket.query_params.get("owner")

    async def identity(*, handshake=False):
        return await run_in_threadpool(
            _guarded_identity, reference, owner, execution_id, handshake=handshake,
        )

    async def authorized():
        try:
            return (await identity()) is not None
        except (SessionExpired, SessionUnavailable, SQLAlchemyError):
            return False

    try:
        connection = await identity(handshake=True)
    except SessionExpired:
        await websocket.close(code=4001)
        return
    except (SessionUnavailable, SQLAlchemyError):
        await websocket.close(code=1013)
        return
    if not connection:
        await websocket.close(code=4003)
        return
    grant, user_id, email = connection
    response = Response()
    set_session_cookie(response, grant)
    headers = [(key, value) for key, value in response.raw_headers if key == b"set-cookie"]
    await manager.connect(websocket, execution_id, authorize=authorized, headers=headers)
    try:
        while True:
            data = await websocket.receive_json()
            if not await manager.authorized(websocket):
                return
            if data.get("event") == "ping":
                await manager.send_personal(websocket, "pong", {})
            elif data.get("event") == "typing":
                await manager.broadcast(
                    execution_id, "user_active", {"user_id": user_id, "email": email},
                    exclude=websocket,
                )
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, execution_id)
