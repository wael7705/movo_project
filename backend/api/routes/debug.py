from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as _select
from ...core.status import compute_current_status
from ...core.db import get_session
from ...models.order import Order
from ...core.db import engine

router = APIRouter()


def _sanitize_db_url() -> str:
    try:
        url = engine.url
        url_str = str(url)
        if getattr(url, "password", None):
            return url_str.replace(url.password, "***")
        return url_str
    except Exception:
        return "unknown"


@router.get("/diag")
async def debug_diag(session: AsyncSession = Depends(get_session)):
    result = await session.execute(_select(Order))
    orders = result.scalars().all()
    counts = {}
    for o in orders:
        cs = compute_current_status(o)
        counts[cs] = counts.get(cs, 0) + 1
    return {"db_url": _sanitize_db_url(), "orders_total": len(orders), "by_status": counts}


