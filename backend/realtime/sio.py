import os
import socketio

REDIS_URL = os.getenv("REDIS_URL")

manager = socketio.AsyncRedisManager(REDIS_URL) if REDIS_URL else None

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    client_manager=manager,
)

# غرف تبويب: tab:<name>
# غرف طلب: order:<id>

@sio.event
async def connect(sid, environ):
    pass

@sio.event
async def join_tab(sid, data):
    tab = (data or {}).get("tab")
    if tab:
        await sio.enter_room(sid, f"tab:{tab}")

@sio.event
async def leave_tab(sid, data):
    tab = (data or {}).get("tab")
    if tab:
        await sio.leave_room(sid, f"tab:{tab}")

@sio.event
async def join_order(sid, data):
    oid = (data or {}).get("order_id")
    if oid:
        await sio.enter_room(sid, f"order:{oid}")

@sio.event
async def leave_order(sid, data):
    oid = (data or {}).get("order_id")
    if oid:
        await sio.leave_room(sid, f"order:{oid}")


async def notify_tab(tab: str, payload: dict):
    # keep existing channel for compatibility
    await sio.emit("notify", payload, room=f"tab:{tab}")
    # emit also to a scoped event name for tab notifications
    await sio.emit(f"notify_tab:{tab}", payload.get("message") if isinstance(payload, dict) else payload)


async def notify_order(order_id: int, payload: dict):
    await sio.emit("notify", payload, room=f"order:{order_id}")
