"""
Order models
نماذج الطلبات
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, ForeignKey, Text, TIMESTAMP, Interval, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.config import Base
from .enums import OrderStatusEnum, PaymentMethodEnum, DeliveryMethodEnum


class Order(Base):
    """Order model"""
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    captain_id = Column(Integer, ForeignKey("captains.captain_id"))
    status = Column(String(50), default=OrderStatusEnum.PENDING)
    payment_method = Column(String(20), default=PaymentMethodEnum.CASH)
    delivery_method = Column(String(20), default=DeliveryMethodEnum.STANDARD)
    time_created = Column(TIMESTAMP(timezone=False), server_default=func.now())
    estimated_delivery_time = Column(Interval)
    distance_meters = Column(Integer)  # Distance between restaurant and customer
    delivery_fee = Column(DECIMAL(10, 2))  # Captain's delivery fee
    total_price_customer = Column(DECIMAL(10, 2))  # Total price including delivery fee
    total_price_restaurant = Column(DECIMAL(10, 2))  # Restaurant invoice (excluding delivery fee)
    cancel_count_per_day = Column(Integer, default=0)
    issue = Column(Text)
    order_note = Column(Text)
    is_scheduled = Column(Boolean, default=False)
    call_restaurant_time = Column(TIMESTAMP(timezone=False))
    select_captain_time = Column(TIMESTAMP(timezone=False))
    expected_delivery_duration = Column(Interval)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("total_price_customer >= 0 AND total_price_restaurant >= 0 AND delivery_fee >= 0"),
        CheckConstraint("cancel_count_per_day >= 0"),
        CheckConstraint("distance_meters >= 0"),
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    captain = relationship("Captain", back_populates="orders")
    stage_durations = relationship("OrderStageDuration", back_populates="order", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="order")
    notes = relationship("Note", back_populates="order")
    issues = relationship("Issue", back_populates="order")
    call_logs = relationship("CallLog", back_populates="order")
    ai_decisions = relationship("AIDecisionLog", back_populates="order")
    ai_failures = relationship("AIFailure", back_populates="order")
    alerts = relationship("AlertLog", back_populates="order")
    order_discounts = relationship("OrderDiscount", back_populates="order", cascade="all, delete-orphan")


class OrderStageDuration(Base):
    """Order stage duration tracking model"""
    __tablename__ = "order_stage_durations"
    
    stage_duration_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    stage_name = Column(String(50), nullable=False)  # pending, accepted, preparing, out_for_delivery, delivered
    stage_start_time = Column(TIMESTAMP(timezone=False), nullable=False)
    stage_end_time = Column(TIMESTAMP(timezone=False))
    duration = Column(Interval)
    stage_status = Column(String(20), default="active")  # active, completed, skipped, cancelled
    stage_metadata = Column(Text)  # JSON data for additional stage info
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="stage_durations")


class OrderDiscount(Base):
    """Order discount relationship model"""
    __tablename__ = "order_discounts"
    
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), primary_key=True)
    discount_id = Column(Integer, ForeignKey("discounts.discount_id", ondelete="CASCADE"), primary_key=True)
    applied_value = Column(DECIMAL(10, 2))  # Actual discount value applied
    
    # Relationships
    order = relationship("Order", back_populates="order_discounts")
    discount = relationship("Discount", back_populates="order_discounts") 