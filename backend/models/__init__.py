from sqlalchemy.orm import declarative_base

Base = declarative_base()

# استيراد النماذج - هذا مهم لضمان عمل النظام
from .customer import Customer
from .restaurant import Restaurant
from .order import Order
from .captain import Captain
from .note import Note
from .rating import Rating

# تصدير النماذج للاستخدام الخارجي
__all__ = ['Base', 'Customer', 'Restaurant', 'Order', 'Captain', 'Note', 'Rating']


