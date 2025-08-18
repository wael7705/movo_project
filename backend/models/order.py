from . import Base
from sqlalchemy import Column, Integer, TIMESTAMP, Boolean, ForeignKey, Numeric, String, Enum
from sqlalchemy.sql import func


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    captain_id = Column(Integer, ForeignKey("captains.captain_id"))

    status = Column(Enum('pending', 'choose_captain', 'processing', 'out_for_delivery', 'delivered', 'cancelled', 'problem', name='order_status_enum'), default="pending")
    current_stage_name = Column(String(50))
    payment_method = Column(Enum('cash', 'card', 'mobile_payment', 'online', name='payment_method_enum'), default='cash')
    delivery_method = Column(Enum('standard', 'express', 'scheduled', 'pick_up', name='delivery_method_enum'), default='standard')
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    is_scheduled = Column(Boolean, default=False)
    scheduled_time = Column(TIMESTAMP(timezone=False))
    
    # حقل مساعد لتحديد قفزة next من pending إلى processing
    is_deferred = Column(Boolean, default=False)

    distance_meters = Column(Integer)
    delivery_fee = Column(Numeric(10, 2))
    total_price_customer = Column(Numeric(10, 2), nullable=False)
    total_price_restaurant = Column(Numeric(10, 2), nullable=False)
    cancel_count_per_day = Column(Integer, default=0)


