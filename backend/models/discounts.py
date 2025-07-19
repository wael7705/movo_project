"""
Discount models
نماذج الحسومات
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.config import Base


class Discount(Base):
    """Discount model"""
    __tablename__ = "discounts"
    
    discount_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # اسم العرض
    description = Column(Text)  # وصف نصي للعرض
    discount_type = Column(String(30), nullable=False)  # نوع الحسم: percentage, fixed, free_delivery, etc.
    value = Column(DECIMAL(10, 2), nullable=False)  # قيمة الحسم (نسبة أو مبلغ)
    is_active = Column(Boolean, default=True)  # هل العرض فعال؟
    start_date = Column(TIMESTAMP(timezone=False))  # تاريخ بداية العرض
    end_date = Column(TIMESTAMP(timezone=False))  # تاريخ نهاية العرض
    code = Column(String(50))  # كود الخصم (إن وجد)
    applies_to_delivery = Column(Boolean, default=False)  # هل ينطبق على التوصيل؟
    applies_to_menu_items = Column(Boolean, default=False)  # هل ينطبق على أصناف محددة؟
    applies_to_entire_menu = Column(Boolean, default=False)  # هل ينطبق على كل الأصناف؟
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id", ondelete="CASCADE"))  # العرض خاص بمطعم معين (اختياري)
    created_by_ai = Column(Boolean, default=False)  # هل تم اقتراح العرض من الذكاء الاصطناعي؟ (مستقبلي)
    ai_recommendation_score = Column(DECIMAL(3, 2))  # درجة توصية الذكاء الاصطناعي (مستقبلي)
    min_order_value = Column(DECIMAL(10, 2))  # الحد الأدنى للطلب (اختياري)
    usage_limit = Column(Integer)  # الحد الأقصى لعدد مرات الاستخدام (اختياري)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="discounts")
    order_discounts = relationship("OrderDiscount", back_populates="discount", cascade="all, delete-orphan") 