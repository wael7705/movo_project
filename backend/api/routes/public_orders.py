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
from pydantic import BaseModel, ConfigDict


class OrderCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    order_id: int
    customer_id: int | None = None
    restaurant_id: int | None = None
    status: str | None = None
    total_price_customer: str | None = None
    delivery_fee: str | None = None
    created_at: str | None = None


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


