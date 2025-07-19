"""
Call log models
نماذج سجل المكالمات
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, Interval
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.config import Base
from .enums import CallStatusEnum


class CallLog(Base):
    """Call log model"""
    __tablename__ = "call_logs"
    
    call_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="SET NULL"))
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="SET NULL"))
    issue_id = Column(Integer, ForeignKey("issues.issue_id", ondelete="SET NULL"))
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"))
    call_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    duration = Column(Interval)  # مدة المكالمة
    call_recording_url = Column(Text)  # رابط لتسجيل المكالمة
    call_type = Column(String(20))  # وارد/صادر/دعم/تسويق...
    notes = Column(Text)  # ملاحظات المكالمة
    
    # Relationships
    order = relationship("Order", back_populates="call_logs")
    customer = relationship("Customer")
    issue = relationship("Issue", back_populates="call_logs")
    employee = relationship("Employee", back_populates="call_logs") 