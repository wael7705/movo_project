"""
Rating models
نماذج التقييمات
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.config import Base


class Rating(Base):
    """Rating model"""
    __tablename__ = "ratings"
    
    rating_id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id", ondelete="CASCADE"))
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    restaurant_emoji_score = Column(Integer)  # تقييم المطعم (1-5)
    order_emoji_score = Column(Integer)  # تقييم الطلب (1-5)
    restaurant_comment = Column(Text)  # تعليق خاص بتقييم المطعم
    order_comment = Column(Text)  # تعليق خاص بتقييم الطلب
    timestamp = Column(TIMESTAMP(timezone=False), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("restaurant_emoji_score BETWEEN 1 AND 5"),
        CheckConstraint("order_emoji_score BETWEEN 1 AND 5"),
        CheckConstraint(
            "(restaurant_id IS NOT NULL AND order_id IS NULL) OR "
            "(restaurant_id IS NULL AND order_id IS NOT NULL)"
        ),
    )
    
    # Relationships
    restaurant = relationship("Restaurant")
    order = relationship("Order", back_populates="ratings") 