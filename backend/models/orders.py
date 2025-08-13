"""
Order model (matches DB table: orders)
"""
from sqlalchemy import (
    Column, Integer, String, DECIMAL, Boolean, ForeignKey,
    TIMESTAMP, Interval, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.config import Base
from .enums import OrderStatusEnum, PaymentMethodEnum, DeliveryMethodEnum
from sqlalchemy import Enum as SAEnum


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    captain_id = Column(Integer, ForeignKey("captains.captain_id"))

    status = Column(
        SAEnum(
            OrderStatusEnum, name="order_status_enum",
            values_callable=lambda e: [x.value for x in e],
            create_type=False, validate_strings=True
        ),
        default=OrderStatusEnum.PENDING,
    )
    payment_method = Column(
        SAEnum(
            PaymentMethodEnum, name="payment_method_enum",
            values_callable=lambda e: [x.value for x in e],
            create_type=False, validate_strings=True
        ),
        default=PaymentMethodEnum.CASH,
    )
    delivery_method = Column(
        SAEnum(
            DeliveryMethodEnum, name="delivery_method_enum",
            values_callable=lambda e: [x.value for x in e],
            create_type=False, validate_strings=True
        ),
        default=DeliveryMethodEnum.STANDARD,
    )

    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    is_scheduled = Column(Boolean, default=False)
    scheduled_time = Column(TIMESTAMP(timezone=False))

    distance_meters = Column(Integer)
    delivery_fee = Column(DECIMAL(10, 2))

    total_price_customer = Column(DECIMAL(10, 2), nullable=False)
    total_price_restaurant = Column(DECIMAL(10, 2), nullable=False)
    cancel_count_per_day = Column(Integer, default=0)

    __table_args__ = (
        CheckConstraint("total_price_customer >= 0 AND total_price_restaurant >= 0 AND delivery_fee >= 0"),
        CheckConstraint("cancel_count_per_day >= 0"),
        CheckConstraint("distance_meters >= 0"),
    )

    # علاقات مهمة
    stage_durations = relationship(
        "OrderStageDuration",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    # علاقة مع توقيتات الطلب
    timings = relationship("OrderTiming", back_populates="order")

    # علاقات أخرى مستخدمة في نماذج أخرى
    customer = relationship("Customer", back_populates="orders", lazy="noload")
    restaurant = relationship("Restaurant", back_populates="orders", lazy="noload")
    captain = relationship("Captain", back_populates="orders", lazy="noload")
    ai_decisions = relationship("AIDecisionLog", back_populates="order", lazy="noload")
    ai_failures = relationship("AIFailure", back_populates="order", lazy="noload")
    alerts = relationship("AlertLog", back_populates="order", lazy="noload")
    notes = relationship("Note", back_populates="order", lazy="noload")
    ratings = relationship("Rating", back_populates="order", lazy="noload")
