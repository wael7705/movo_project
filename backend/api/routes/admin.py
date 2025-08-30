from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Dict, Any, List

from core.db import get_session
from models.order import Order
from models.captain import Captain
from models.restaurant import Restaurant
from realtime.sio import sio

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/counters")
async def counters(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Order))
    orders = result.scalars().all()
    tabs = ["pending", "assign", "processing", "out_for_delivery", "delivered", "cancelled", "issue"]
    counts = {k: 0 for k in tabs}
    for o in orders:
        # naive mapping
        st = (o.status or '').lower().strip()
        if st == 'choose_captain':
            st = 'assign'
        if st not in counts:
            if st == 'problem':
                st = 'issue'
            else:
                st = 'pending'
        counts[st] += 1
    return counts


@router.get("/captains/live")
async def captains_live(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Captain))
    rows: List[Captain] = result.scalars().all()
    out = []
    for c in rows:
        out.append({
            "id": c.captain_id,
            "name": c.name,
            "lat": float(c.last_lat or 33.5138),
            "lng": float(c.last_lng or 36.2765),
            "status": 'active' if c.available else 'offline',
            "orders_now": 0,
            "delivered_today": int(c.orders_delivered or 0),
            "vehicle": c.vehicle_type,
            "rating": float(c.performance or 5.0),
        })
    return out


class Toggle(BaseModel):
    visible: bool


@router.get("/restaurants")
async def list_restaurants(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Restaurant))
    rows: List[Restaurant] = result.scalars().all()
    return [
        {
            "id": r.restaurant_id,
            "name": r.name,
            "lat": float(r.latitude),
            "lng": float(r.longitude),
            "visible": bool(getattr(r, 'visible', True)),
        }
        for r in rows
    ]


@router.patch("/restaurant/{rid}/visible")
async def toggle_restaurant(rid: int, body: Toggle, session: AsyncSession = Depends(get_session)):
    obj = (await session.execute(select(Restaurant).where(Restaurant.restaurant_id == rid))).scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    setattr(obj, 'visible', bool(body.visible))
    await session.commit()
    return {"ok": True, "id": rid, "visible": bool(body.visible)}


@router.patch("/category/{cid}/visible")
async def toggle_category(cid: int, body: Toggle):
    return {"ok": True, "id": cid, "visible": bool(body.visible)}


@router.patch("/addon/{aid}/visible")
async def toggle_addon(aid: int, body: Toggle):
    return {"ok": True, "id": aid, "visible": bool(body.visible)}


class Notify(BaseModel):
    tab: str
    message: str


@router.post("/notify")
async def notify(body: Notify):
    room = f"notify_tab:{body.tab}"
    await sio.emit(room, body.message, namespace="/")
    return {"ok": True}


@router.get("/restaurant/{rid}/stats")
async def restaurant_stats(rid: int, session: AsyncSession = Depends(get_session)):
    total_today_q = (
        select(func.count()).select_from(Order).where(
            (Order.restaurant_id == rid)
            & (func.date_trunc('day', Order.created_at) == func.date_trunc('day', func.now()))
        )
    )
    total_week_q = (
        select(func.count()).select_from(Order).where(
            (Order.restaurant_id == rid)
            & (Order.created_at >= func.now() - text("INTERVAL '7 days'"))
        )
    )
    total_today = int((await session.execute(total_today_q)).scalar() or 0)
    total_week = int((await session.execute(total_week_q)).scalar() or 0)
    return {
        "rating": 4.5,
        "orders_today": total_today,
        "orders_week": total_week,
        "profit_margin": 0.18,
    }


