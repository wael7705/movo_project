from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.order import Order
from app.schemas.order import OrderRead, OrderCreate


router = APIRouter()


@router.get("", response_model=List[OrderRead])
async def list_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    return [OrderRead.model_validate(o, from_attributes=True) for o in orders]


@router.post("", response_model=OrderRead, status_code=201)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    order = Order(customer_name=payload.customer_name, items=payload.items, status=payload.status or "pending")
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return OrderRead.model_validate(order, from_attributes=True)


