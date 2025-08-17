"""
Customer models
نماذج العملاء
"""

from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from ..database.config import Base
from .enums import MembershipTypeEnum, AddressTypeEnum


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    membership_type = Column(String(20), default=MembershipTypeEnum.NORMAL)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="customer")
    
    # Relationships
    addresses = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer")


class CustomerAddress(Base):
    """Customer address model"""
    __tablename__ = "customer_addresses"
    
    address_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"))
    address_type = Column(String(20), default=AddressTypeEnum.HOME)
    city = Column(String(100), nullable=False)
    street = Column(String(200), nullable=False)
    district = Column(String(100))
    neighborhood = Column(String(100))
    additional_details = Column(Text)
    extra_details = Column(Text)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    is_default = Column(Boolean, default=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="addresses") 