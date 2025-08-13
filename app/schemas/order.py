from datetime import datetime
from typing import List, Any, Optional

from pydantic import BaseModel, ConfigDict


class OrderBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    customer_name: str
    items: List[Any]
    status: Optional[str] = "pending"


class OrderCreate(OrderBase):
    pass


class OrderRead(OrderBase):
    id: int
    created_at: Optional[datetime] = None


