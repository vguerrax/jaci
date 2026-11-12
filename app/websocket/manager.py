import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any
from fastapi import WebSocket

logger = logging.getLogger("jaci.ws")


class ConnectionManager:
    """
    Gerenciador de conexões WebSocket.
    Agrupa conexões por execution_id para broadcast seletivo.
    """

    def __init__(self):
        # execution_id -> set de WebSockets
        self._rooms: dict[int, set[WebSocket]] = {}
        self._checks: dict[WebSocket, Callable[[], Awaitable[bool]]] = {}

    async def connect(
        self, websocket: WebSocket, execution_id: int, *, authorize=None, headers=(),
    ) -> None:
        """Aceita a conexão e registra na sala."""
        if headers:
            await websocket.accept(headers=headers)
        else:
            await websocket.accept()
        if authorize:
            self._checks[websocket] = authorize
        if execution_id not in self._rooms:
            self._rooms[execution_id] = set()
        self._rooms[execution_id].add(websocket)
        logger.info(
            f"WebSocket conectado à execução {execution_id} "
            f"(total: {len(self._rooms[execution_id])})"
        )

    def disconnect(self, websocket: WebSocket, execution_id: int) -> None:
        """Remove a conexão da sala."""
        self._checks.pop(websocket, None)
        if execution_id in self._rooms:
            self._rooms[execution_id].discard(websocket)
            if not self._rooms[execution_id]:
                del self._rooms[execution_id]
            logger.info(f"WebSocket desconectado da execução {execution_id}")

    async def broadcast(
        self,
        execution_id: int,
        event: str,
        data: dict[str, Any],
        exclude: WebSocket | None = None,
    ) -> None:
        """
        Envia mensagem para todos na sala, exceto o remetente (se informado).
        Formato: {"event": "...", "data": {...}}
        """
        if execution_id not in self._rooms:
            return

        message = json.dumps({"event": event, "data": data})
        disconnected = set()

        for ws in tuple(self._rooms[execution_id]):
            if ws == exclude:
                continue
            try:
                if await self.authorized(ws):
                    await ws.send_text(message)
                else:
                    disconnected.add(ws)
            except Exception:
                disconnected.add(ws)

        # Limpa conexões mortas
        for ws in disconnected:
            self.disconnect(ws, execution_id)

    async def authorized(self, websocket: WebSocket) -> bool:
        check = self._checks.get(websocket)
        if check is None or await check():
            return True
        await websocket.close(code=4001)
        return False

    async def send_personal(
        self,
        websocket: WebSocket,
        event: str,
        data: dict[str, Any],
    ) -> None:
        """Envia mensagem para um único cliente."""
        message = json.dumps({"event": event, "data": data})
        try:
            await websocket.send_text(message)
        except Exception:
            pass


# Instância global
manager = ConnectionManager()
