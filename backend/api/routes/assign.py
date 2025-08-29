from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from math import radians, sin, cos, asin, sqrt
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import asyncio

from core.db import get_session
from models.order import Order
from models.restaurant import Restaurant
from models.captain import Captain
from .ws import manager


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
            out.append(
                Candidate(
                    captain_id=c.captain_id,
                    captain_name=c.name,
                    last_lat=lat,
                    last_lng=lng,
                    active_orders=0,
                    distance_km=round(d, 2),
                    last_order_ids=[],
                )
            )

    out.sort(key=lambda x: (x.distance_km, x.active_orders))
    return out


class AssignIn(BaseModel):
    captain_id: int


@router.post("/orders/{order_id}/assign")
async def assign(order_id: int, body: AssignIn, session: AsyncSession = Depends(get_session)):
    # ثبّت التعيين: اربط الكابتن بالطلب واحفظ حالة التبويب الحالية
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, detail="Order not found")
    # إذا كان لدى Order حقول captain_id/current_status فحدّثها بأمان
    try:
        if hasattr(order, 'captain_id'):
            setattr(order, 'captain_id', body.captain_id)
        if hasattr(order, 'status'):
            # أبقه في choose_captain بانتظار قبول الكابتن (واجهه ستعرض Awaiting)
            setattr(order, 'status', 'choose_captain')
        if hasattr(order, 'current_status'):
            setattr(order, 'current_status', 'choose_captain')
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    # جدولة إرسال قبول عبر WS بعد 3 ثوانٍ — محاكاة رد الكابتن الفعلي
    try:
        asyncio.create_task(
            manager.send_json_after(
                body.captain_id,
                {"type": "accepted", "captain_id": body.captain_id, "order_id": order_id},
                3.0,
            )
        )
    except Exception:
        pass
    return {"ok": True}


