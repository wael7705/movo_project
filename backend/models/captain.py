from . import Base
from sqlalchemy import Column, Integer, String, Boolean, Numeric, TIMESTAMP
from sqlalchemy.sql import func


class Captain(Base):
    __tablename__ = "captains"

    captain_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    alt_phone = Column(String(20))
    vehicle_type = Column(String(50), nullable=False)
    orders_delivered = Column(Integer, default=0)
    performance = Column(Numeric(3, 2), default=5.00)
    available = Column(Boolean, default=True)
    # إحداثيات آخر موقع (للتتبع الحي)
    last_lat = Column(Numeric(10, 8))
    last_lng = Column(Numeric(11, 8))
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now())

