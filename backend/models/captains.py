"""
Captain models
نماذج الكباتن
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database.config import Base


class Captain(Base):
    """Captain model"""
    __tablename__ = "captains"
    
    captain_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    alt_phone = Column(String(20))
    vehicle_type = Column(String(50), nullable=False)
    orders_delivered = Column(Integer, default=0)
    performance = Column(Float, default=5.00)  # Rating out of 5
    available = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="captain")
    
    # Relationships
    orders = relationship("Order", back_populates="captain") 