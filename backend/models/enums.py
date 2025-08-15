"""
Enum types for MOVO delivery platform
أنواع التعداد المستخدمة في منصة MOVO للتوصيل
"""

from enum import Enum


class MembershipTypeEnum(str, Enum):
    """Customer membership types"""
    NORMAL = "normal"
    VIP = "vip"
    MOVO_PLUS = "movo_plus"


class RestaurantStatusEnum(str, Enum):
    """Restaurant status"""
    ONLINE = "online"
    OFFLINE = "offline"


class RestaurantAvailabilityEnum(str, Enum):
    """Restaurant availability"""
    AVAILABLE = "available"
    BUSY = "busy"


class OrderStatusEnum(str, Enum):
    """Order status"""
    PENDING = "pending"
    CHOOSE_CAPTAIN = "choose_captain"
    CAPTAIN_ASSIGNED = "captain_assigned"
    PROCESSING = "processing"
    WAITING_APPROVAL = "waiting_approval"
    PREPARING = "preparing"
    CAPTAIN_RECEIVED = "captain_received"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    PROBLEM = "problem"
    DELAYED = "delayed"
    ACCEPTED = "accepted"
    WAITING_RESTAURANT_ACCEPTANCE = "waiting_restaurant_acceptance"
    PICK_UP_READY = "pick_up_ready"


class PhoneTypeEnum(str, Enum):
    """Phone number types"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    WHATSAPP = "whatsapp"
    BUSINESS = "business"
    ADMIN = "admin"


class AddressTypeEnum(str, Enum):
    """Address types"""
    HOME = "home"
    WORK = "work"
    OTHER = "other"


class NoteTypeEnum(str, Enum):
    """Note types"""
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    CAPTAIN = "captain"
    ORDER = "order"
    ISSUE = "issue"


class NoteTargetEnum(str, Enum):
    """Note target types"""
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    CAPTAIN = "captain"
    ORDER = "order"
    ISSUE = "issue"


class PaymentMethodEnum(str, Enum):
    """Payment methods"""
    CASH = "cash"
    CARD = "card"
    MOBILE_PAYMENT = "mobile_payment"
    ONLINE = "online"


class DeliveryMethodEnum(str, Enum):
    """Delivery methods"""
    STANDARD = "standard"
    EXPRESS = "express"
    SCHEDULED = "scheduled"
    PICK_UP = "pick_up"


class EmployeeRoleEnum(str, Enum):
    """Employee roles"""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    STAFF = "staff"


class CallStatusEnum(str, Enum):
    """Call status for call logs"""
    MISSED = "missed"
    COMPLETED = "completed"
    REJECTED = "rejected" 