from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    customer_id: Optional[int]
    restaurant_id: Optional[int]
    status: str
    total_price_customer: Optional[str]
    delivery_fee: Optional[str]
    created_at: Optional[str]
    current_status: Literal[
        "pending",
        "choose_captain",
        "processing",
        "out_for_delivery",
        "delivered",
        "cancelled",
        "problem",
    ]
    substage: Optional[str] = None


