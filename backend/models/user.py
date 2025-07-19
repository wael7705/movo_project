from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.database.config import Base

class UserRole(str, enum.Enum):
    customer = "customer"
    captain = "captain"
    restaurant = "restaurant"
    data_entry = "data_entry"
    call_center_agent = "call_center_agent"
    call_center_supervisor = "call_center_supervisor"
    admin = "admin"
    ai = "ai"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    role = Column(SqlEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    device_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # علاقات مع الجداول الأخرى (اختياري)
    customer = relationship("Customer", back_populates="user", uselist=False)
    captain = relationship("Captain", back_populates="user", uselist=False)
    restaurant = relationship("Restaurant", back_populates="user", uselist=False) 