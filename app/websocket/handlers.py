import logging
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
 
from app.database import SessionLocal
from app.dependencies import get_current_user_ws
from app.websocket.manager import manager
from app.models.user import User
from app.models.execution import ExecutionItem
from app.services.execution_service import get_execution_by_id
 
logger = logging.getLogger("jaci.ws")
 
 
async def execution_ws_handler(
    websocket: WebSocket,
    execution_id: int,
    token: str | None = None,
):
    """
    Gerencia a conexão WebSocket para uma execução específica.
    Autentica via token JWT (query param ou cookie).
    """
    # Autentica o usuário
    db = SessionLocal()
    user = None
    try:
        if token:
            from app.utils.security import decode_access_token
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    user = db.scalar(
                        select(User).where(User.id == int(user_id))
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