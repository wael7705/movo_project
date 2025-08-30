import json
from typing import Dict, Any
from .sio import sio


async def notify_tab(tab: str, payload: Dict[str, Any]) -> None:
    try:
        await sio.emit("notify", payload, room=f"tab:{tab}")
    except Exception:
        # في حال عدم تفعيل Socket.IO أو مشاكل، نتجاهل الخطأ بصمت
        pass


