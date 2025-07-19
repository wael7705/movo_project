from fastapi_users.schemas import BaseUser, BaseUserCreate
from typing import Optional
from datetime import datetime

class UserRead(BaseUser[int]):
    phone: str
    role: str
    device_id: Optional[str]
    created_at: datetime
    # أضف أي حقول إضافية مطلوبة هنا

class UserCreate(BaseUserCreate):
    phone: str
    role: str
    device_id: Optional[str] = None
    # أضف أي حقول إضافية مطلوبة هنا 