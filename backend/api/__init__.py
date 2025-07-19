"""
API package initialization
تهيئة حزمة API
"""

from .routes.orders import router as orders_router
from .routes.chat import router as chat_router
from .routes.captains import router as captains_router
from .routes.restaurants import router as restaurants_router
from .routes.customers import router as customers_router
from .routes.analytics import router as analytics_router

__all__ = [
    'orders_router',
    'chat_router',
    'captains_router',
    'restaurants_router',
    'customers_router',
    'analytics_router'
] 
