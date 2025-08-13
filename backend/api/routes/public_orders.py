"""
Public Orders API routes
مسار عام لإرجاع قائمة بطاقات الطلبات بدون مصادقة
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.database import get_db
from backend.models.orders import Order
from backend.schemas.order import OrderCard


router = APIRouter()


@router.get("/orders", response_model=List[OrderCard], tags=["Orders"])
async def list_public_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Order).offset(skip).limit(limit))
    orders = result.scalars().all()
    return [OrderCard.model_validate(order, from_attributes=True) for order in orders]


