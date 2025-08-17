"""
Restaurant models
نماذج المطاعم
"""

from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP
from ..database.config import Base
from .enums import RestaurantStatusEnum, RestaurantAvailabilityEnum, PhoneTypeEnum


class Restaurant(Base):
    """Restaurant model"""
    __tablename__ = "restaurants"
    
    restaurant_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    restaurant_location = Column(String(200))
    status = Column(String(20), default=RestaurantStatusEnum.OFFLINE)
    availability = Column(String(20), default=RestaurantAvailabilityEnum.AVAILABLE)
    estimated_preparation_time = Column(Integer, nullable=False)  # in minutes
    price_matches = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="restaurant")
    
    # Relationships
    phones = relationship("RestaurantPhone", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant")
    discounts = relationship("Discount", back_populates="restaurant")


class RestaurantPhone(Base):
    """Restaurant phone model"""
    __tablename__ = "restaurant_phones"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id", ondelete="CASCADE"))
    phone = Column(String(20), nullable=False)
    phone_type = Column(String(20), default=PhoneTypeEnum.PRIMARY)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="phones")


class MenuItem(Base):
    """Menu item model"""
    __tablename__ = "menu_items"
    
    item_id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id", ondelete="CASCADE"))
    name_item = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    extras = Column(JSON)  # Array of objects: [{"name": "Cheese", "price": 2.0}]
    discount_percentage = Column(DECIMAL(5, 2), default=0)  # نسبة الحسم على الصنف (0-100)
    is_visible = Column(Boolean, default=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    options = relationship("MenuItemOption", back_populates="menu_item", cascade="all, delete-orphan")


class MenuItemOption(Base):
    """Menu item option model"""
    __tablename__ = "menu_item_options"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("menu_items.item_id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)  # اسم الإضافة مثل "زيادة جبنة"
    price = Column(DECIMAL(10, 2), nullable=False)  # سعر الإضافة
    is_available = Column(Boolean, default=True)  # هل الإضافة متاحة حالياً؟
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())
    
    # Relationships
    menu_item = relationship("MenuItem", back_populates="options") 