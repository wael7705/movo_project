"""
SQLAlchemy models for MOVO delivery platform
نماذج SQLAlchemy لمنصة MOVO للتوصيل
"""

# Import Base from database config
from ..database.config import Base

from .chat_message import ChatMessage

# Import enums first
from .enums import (
    MembershipTypeEnum, RestaurantStatusEnum, RestaurantAvailabilityEnum,
    OrderStatusEnum, PhoneTypeEnum, AddressTypeEnum, NoteTypeEnum,
    NoteTargetEnum, PaymentMethodEnum, DeliveryMethodEnum, EmployeeRoleEnum,
    CallStatusEnum
)

# Import all models to register them with SQLAlchemy
from .customers import Customer, CustomerAddress
from .restaurants import Restaurant, RestaurantPhone, MenuItem, MenuItemOption
from .orders import Order, OrderStageDuration, OrderDiscount
from .captains import Captain
from .weather import WeatherLog
from .ratings import Rating
from .notes import Note
from .employees import Employee
from .issues import Issue
from .call_logs import CallLog
from .discounts import Discount
from .ai_analytics import AIDecisionLog, AIFailure, AlertLog

__all__ = [
    # Enums
    "MembershipTypeEnum", "RestaurantStatusEnum", "RestaurantAvailabilityEnum",
    "OrderStatusEnum", "PhoneTypeEnum", "AddressTypeEnum", "NoteTypeEnum",
    "NoteTargetEnum", "PaymentMethodEnum", "DeliveryMethodEnum", "EmployeeRoleEnum",
    "CallStatusEnum",
    
    # Core Models
    "Customer", "CustomerAddress", "Restaurant", "RestaurantPhone",
    "MenuItem", "MenuItemOption", "Order", "OrderStageDuration",
    "Captain", "WeatherLog", "Rating", "Note",
    
    # Business Models
    "Employee", "Issue", "CallLog", "Discount", "OrderDiscount",
    
    # AI & Analytics
    "AIDecisionLog", "AIFailure", "AlertLog",
    # Chat
    "ChatMessage",
] 