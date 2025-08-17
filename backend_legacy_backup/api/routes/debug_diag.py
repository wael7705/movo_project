"""
Debug diagnostics endpoint to verify database connection and order counts.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as _select
from typing import Dict, Any

from ...database.database import get_db
from ...database.config import engine
from ...models.orders import Order

router = APIRouter()


def _sanitize_db_url() -> str:
    try:
        url = engine.url
        url_str = str(url)
        # Hide password if present
        if getattr(url, "password", None):
            return url_str.replace(url.password, "***")
        return url_str
    except Exception:
        return "unknown"


def _compute_current_status(o: Any) -> str:
    real = getattr(o, 'status', None)
    real = getattr(real, 'value', real)
    real = str(real) if real is not None else ''
    if real == 'cancelled':
        return 'cancelled'
    if real == 'delivered':
        return 'delivered'
    if real == 'out_for_delivery':
        return 'out_for_delivery'
    if real in {'accepted', 'captain_assigned', 'choose_captain'}:
        return 'choose_captain'
    if real in {'processing', 'waiting_approval', 'preparing', 'captain_received'}:
        return 'processing'
    if real == 'problem':
        return 'problem'
    return 'pending'


@router.get("/_debug/diag", response_model=Dict[str, Any])
async def debug_diag(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    result = await db.execute(_select(Order))
    orders = result.scalars().all()
    by_status: Dict[str, int] = {}
    for o in orders:
        label = _compute_current_status(o)
        by_status[label] = by_status.get(label, 0) + 1
    return {
        "db_url": _sanitize_db_url(),
        "orders_total": len(orders),
        "by_status": by_status,
    }


