from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import random
import contextlib

router = APIRouter(tags=["realtime"])


class ConnectionManager:
    def __init__(self):
        self.active: Dict[int, Set[WebSocket]] = {}

    async def connect(self, captain_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(captain_id, set()).add(websocket)

    def disconnect(self, captain_id: int, websocket: WebSocket):
        conns = self.active.get(captain_id)
        if not conns:
            return
        with contextlib.suppress(KeyError):
            conns.remove(websocket)
        if not conns:
            self.active.pop(captain_id, None)

    async def send_json(self, captain_id: int, data: dict):
        for ws in list(self.active.get(captain_id, set())):
            with contextlib.suppress(Exception):
                await ws.send_json(data)

    async def send_json_after(self, captain_id: int, data: dict, delay_sec: float):
        await asyncio.sleep(delay_sec)
        await self.send_json(captain_id, data)


manager = ConnectionManager()


@router.websocket("/ws/captain/{captain_id}")
async def ws_captain(websocket: WebSocket, captain_id: int):
    await manager.connect(captain_id, websocket)

    async def _pos_loop():
        base_lat = 33.5138 + random.uniform(-0.01, 0.01)
        base_lng = 36.2765 + random.uniform(-0.01, 0.01)
        while True:
            base_lat += random.uniform(-0.0005, 0.0005)
            base_lng += random.uniform(-0.0005, 0.0005)
            await manager.send_json(
                captain_id,
                {"type": "pos", "captain_id": captain_id, "lat": base_lat, "lng": base_lng},
            )
            await asyncio.sleep(1)

    pos_task = asyncio.create_task(_pos_loop())
    try:
        while True:
            msg = await websocket.receive_json()
            if isinstance(msg, dict) and msg.get("type") == "assign":
                order_id = msg.get("order_id")
                # أرسل قبول بعد 3 ثواني عبر WS
                asyncio.create_task(
                    manager.send_json_after(
                        captain_id,
                        {"type": "accepted", "captain_id": captain_id, "order_id": order_id},
                        3.0,
                    )
                )
    except WebSocketDisconnect:
        pass
    finally:
        pos_task.cancel()
        with contextlib.suppress(Exception):
            await pos_task
        manager.disconnect(captain_id, websocket)


