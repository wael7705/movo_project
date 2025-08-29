import os
import socketio

REDIS_URL = os.getenv("REDIS_URL")
SOCKET_IO_PATH = os.getenv("SOCKET_IO_PATH", "socket.io")

manager = socketio.AsyncRedisManager(REDIS_URL) if REDIS_URL else None

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_timeout=25,
    ping_interval=20,
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
    await sio.emit("notify", payload, room=f"tab:{tab}")


async def notify_order(order_id: int, payload: dict):
    await sio.emit("notify", payload, room=f"order:{order_id}")
