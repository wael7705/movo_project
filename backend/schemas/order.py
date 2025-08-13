"""
Pydantic v2 schemas for Orders
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrderCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    customer_id: Optional[int] = None
    restaurant_id: Optional[int] = None
    captain_id: Optional[int] = None
    status: Optional[str] = None
    total_price_customer: Optional[Decimal] = None
    delivery_fee: Optional[Decimal] = None
    created_at: Optional[datetime] = None


