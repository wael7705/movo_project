"""
Order stage durations (matches DB table: order_stage_durations)
"""
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Interval
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.config import Base


class OrderStageDuration(Base):
    tablename = "order_stage_durations"

    stage_duration_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), index=True)
    stage_name = Column(String(50), nullable=False)  # pending / accepted / preparing / out_for_delivery / delivered
    duration = Column(Interval)
    recorded_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)

    # علاقة مع الطلب
    order = relationship("Order", back_populates="stage_durations")