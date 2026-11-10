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
