from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List
from math import radians, sin, cos, asin, sqrt
import random

from sqlalchemy import select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import asyncio
import json

from core.db import get_session
from models.order import Order
from models.restaurant import Restaurant
from models.captain import Captain
from .ws import manager
from core.redis import get_redis


router = APIRouter(prefix="/api/v1/assign", tags=["assign"])


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))


class Candidate(BaseModel):
    captain_id: int
    captain_name: str
    last_lat: float
    last_lng: float
    active_orders: int
    distance_km: float
    eta_sec: int | None = None
    score: float | None = None
    last_order_ids: List[int] = []


@router.get("/orders/{order_id}/candidates", response_model=List[Candidate])
async def candidates(order_id: int, radius_km: float = 5, session: AsyncSession = Depends(get_session)):
    # احصل على الطلب والمطعم
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, detail="Order not found")

    result = await session.execute(select(Restaurant).where(Restaurant.restaurant_id == order.restaurant_id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(404, detail="Restaurant not found")

    ref_lat = float(restaurant.latitude)
    ref_lng = float(restaurant.longitude)

    # أحضر كباتن متاحين
    result = await session.execute(select(Captain).where(Captain.available == True))
    captains = result.scalars().all()

    out: List[Candidate] = []
    for c in captains:
        # استخدم last_lat/last_lng إن توفّرت، وإلا ولّد إحداثيات قريبة مؤقتاً
        if c.last_lat is not None and c.last_lng is not None:
            lat = float(c.last_lat)
            lng = float(c.last_lng)
        else:
            lat = ref_lat + random.uniform(-0.01, 0.01)
            lng = ref_lng + random.uniform(-0.01, 0.01)
        d = haversine_km(ref_lat, ref_lng, lat, lng)
        if d <= radius_km:
            # تقدير ETA بسيط: سرعة افتراضية 25 كم/ساعة + 60 ثانية ثابتة
            avg_speed_kmh = 25.0
            travel_hours = d / avg_speed_kmh
            eta_sec = int(travel_hours * 3600 + 60)
            # سكور: أقرب مسافة وأقل حمل أفضل
            active_orders = 0
            score = max(0.0, 1.0 - (d / radius_km)) + (0.5 if active_orders == 0 else 0.0)
            out.append(
                Candidate(
                    captain_id=c.captain_id,
                    captain_name=c.name,
                    last_lat=lat,
                    last_lng=lng,
                    active_orders=active_orders,
                    distance_km=round(d, 2),
                    eta_sec=eta_sec,
                    score=round(score, 3),
                    last_order_ids=[],
                )
            )

    # رتب حسب score ثم المسافة
    out.sort(key=lambda x: (-(x.score or 0), x.distance_km))
    return out


class AssignIn(BaseModel):
    captain_id: int


@router.post("/orders/{order_id}/assign")
async def assign(order_id: int, body: AssignIn, session: AsyncSession = Depends(get_session), Idempotency_Key: str | None = Header(default=None)):
    # تحقق idempotency اختياري: إذا تم إرسال نفس المفتاح سابقًا، نتجاهل التكرار
    if Idempotency_Key:
        try:
            await session.execute(sa_text("INSERT INTO idempotency_keys(key) VALUES (:k) ON CONFLICT DO NOTHING"), {"k": Idempotency_Key})
            rows = (await session.execute(sa_text("SELECT key FROM idempotency_keys WHERE key=:k"), {"k": Idempotency_Key})).all()
            if not rows:
                return {"ok": True, "duplicate": True}
        except Exception:
            pass
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, detail="Order not found")
    try:
        if hasattr(order, 'captain_id'):
            setattr(order, 'captain_id', body.captain_id)
        if hasattr(order, 'status'):
            setattr(order, 'status', 'choose_captain')
        if hasattr(order, 'current_status'):
            setattr(order, 'current_status', 'choose_captain')
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    # بثّ حدث التعيين عبر Redis (اختياري)
    try:
        r = await get_redis()
        if r:
            channel = f"captain:{body.captain_id}"
            await r.publish(channel, json.dumps({"type": "assigned", "order_id": order_id, "captain_id": body.captain_id}))
        # سجل الحدث في order_events
        await session.execute(sa_text("INSERT INTO order_events(order_id, event_type, payload) VALUES (:oid, 'assigned', CAST(:p AS JSONB))"), {"oid": order_id, "p": json.dumps({"captain_id": body.captain_id})})
        await session.commit()
    except Exception:
        pass

    # إرسال قبول محاكى بعد 3 ثوانٍ عبر WS
    try:
        asyncio.create_task(
            manager.send_json_after(
                body.captain_id,
                {"type": "accepted", "captain_id": body.captain_id, "order_id": order_id},
                3.0,
            )
        )
        # سجل accepted أيضاً
        await session.execute(sa_text("INSERT INTO order_events(order_id, event_type, payload) VALUES (:oid, 'accepted', CAST(:p AS JSONB))"), {"oid": order_id, "p": json.dumps({"captain_id": body.captain_id})})
        await session.commit()
    except Exception:
        pass
    return {"ok": True}


class StartDeliveryBody(BaseModel):
    captain_id: int
    restaurant: dict | None = None
    customer: dict | None = None


@router.post("/orders/{order_id}/test/accept")
async def test_accept(order_id: int, body: AssignIn):
    # إرسال قبول تجريبي عبر Socket.IO بعد 1 ثانية
    asyncio.create_task(
        manager.send_json_after(
            body.captain_id,
            {"type": "accepted", "captain_id": body.captain_id, "order_id": order_id},
            1.0,
        )
    )
    return {"ok": True}


@router.post("/orders/{order_id}/test/start_delivery")
async def test_start_delivery(order_id: int, body: StartDeliveryBody):
    cpt = body.captain_id
    r = body.restaurant or {"lat": 33.5138, "lng": 36.2765}
    c = body.customer or {"lat": 33.515, "lng": 36.28}

    r_lat = float(r.get('lat', 33.5138))
    r_lng = float(r.get('lng', 36.2765))
    c_lat = float(c.get('lat', 33.515))
    c_lng = float(c.get('lng', 36.28))

    async def _route_loop():
        steps = 30
        for i in range(steps + 1):
            t = i / steps
            lat = r_lat + (c_lat - r_lat) * t
            lng = r_lng + (c_lng - r_lng) * t
            await manager.send_json(cpt, { 'type': 'pos', 'captain_id': cpt, 'lat': lat, 'lng': lng })
            await asyncio.sleep(1)
        await manager.send_json(cpt, { 'type': 'delivered', 'captain_id': cpt })

    asyncio.create_task(_route_loop())
    return {"ok": True}


