from sqlalchemy import Column, Integer, ForeignKey, Interval, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.config import Base

class OrderTiming(Base):
    __tablename__ = "order_timings"

    timing_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    expected_preparation_time = Column("expected_preparation_time", Interval, nullable=False)
    expected_delivery_duration = Column("expected_delivery_duration", Interval, nullable=False)
    total_expected_duration = Column("total_expected_duration", Interval, nullable=False)
    actual_processing_time = Column(Interval)
    actual_delivery_time = Column(Interval)
    estimated_delivery_time = Column("estimated_delivery_time", TIMESTAMP)

    # Relationship
    order = relationship("Order", back_populates="timing") 