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

    async def _route_loop(r_lat: float, r_lng: float, c_lat: float, c_lng: float):
        steps = 30
        for i in range(steps + 1):
            t = i / steps
            lat = r_lat + (c_lat - r_lat) * t
            lng = r_lng + (c_lng - r_lng) * t
            await manager.send_json(
                captain_id,
                {"type": "pos", "captain_id": captain_id, "lat": lat, "lng": lng},
            )
            await asyncio.sleep(1)
        # عند الوصول، أرسل delivered
        await manager.send_json(
            captain_id,
            {"type": "delivered", "captain_id": captain_id},
        )

    pos_task = asyncio.create_task(_pos_loop())
    route_task = None
    try:
        while True:
            msg = await websocket.receive_json()
            if not isinstance(msg, dict):
                continue
            mtype = msg.get("type")
            if mtype == "assign":
                order_id = msg.get("order_id")
                asyncio.create_task(
                    manager.send_json_after(
                        captain_id,
                        {"type": "accepted", "captain_id": captain_id, "order_id": order_id},
                        3.0,
                    )
                )
            elif mtype == "start_delivery":
                # أوقف بث الموضع العشوائي
                if pos_task and not pos_task.done():
                    pos_task.cancel()
                    with contextlib.suppress(Exception):
                        await pos_task
                rest = msg.get("restaurant") or {}
                cust = msg.get("customer") or {}
                r_lat = float(rest.get("lat", 33.5138))
                r_lng = float(rest.get("lng", 36.2765))
                c_lat = float(cust.get("lat", 33.515))
                c_lng = float(cust.get("lng", 36.28))
                # ابدأ مسار مباشر من المطعم إلى الزبون
                route_task = asyncio.create_task(_route_loop(r_lat, r_lng, c_lat, c_lng))
            elif mtype == "stop_delivery":
                if route_task and not route_task.done():
                    route_task.cancel()
                    with contextlib.suppress(Exception):
                        await route_task
                # استئناف البث العشوائي
                if (not pos_task) or pos_task.done():
                    pos_task = asyncio.create_task(_pos_loop())
    except WebSocketDisconnect:
        pass
    finally:
        if route_task and not route_task.done():
            route_task.cancel()
            with contextlib.suppress(Exception):
                await route_task
        if pos_task and not pos_task.done():
            pos_task.cancel()
            with contextlib.suppress(Exception):
                await pos_task
        manager.disconnect(captain_id, websocket)


