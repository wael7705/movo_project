from sqlalchemy import Column, Integer, ForeignKey, Interval, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from ..database.config import Base

class OrderTiming(Base):
    __tablename__ = "order_timings"

    timing_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    expected_preparation_time = Column(Interval, nullable=False)
    expected_delivery_duration = Column(Interval, nullable=False)
    # حساب تلقائي (إذا أردت استخدامه في بايثون)
    @hybrid_property
    def total_expected_duration_calc(self):
        if self.expected_preparation_time and self.expected_delivery_duration:
            from datetime import timedelta
            return self.expected_preparation_time + self.expected_delivery_duration + timedelta(minutes=6)
        return None
    actual_processing_time = Column(Interval)
    actual_delivery_time = Column(Interval)
    estimated_delivery_time = Column(TIMESTAMP)

    # Relationship
    order = relationship("Order", back_populates="timing") 