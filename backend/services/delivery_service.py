"""
Advanced delivery service with AI support for MOVO delivery platform
خدمة التوصيل المتقدمة مع دعم الذكاء الاصطناعي لمنصة MOVO للتوصيل
"""

import math
import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from backend.models import Order, Captain
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class DeliveryService:
    """Advanced service for delivery-related operations with AI support"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_delivery_fee(self, distance_km: float, order_value: float = 0, 
                                   weather_factor: float = 1.0, time_factor: float = 1.0) -> Dict[str, Any]:
        """
        Calculate delivery fee with advanced factors including weather and time
        حساب رسوم التوصيل مع عوامل متقدمة تشمل الطقس والوقت
        """
        try:
            # Base fee
            base_fee = 5.0
            
            # Distance fee (2 SAR per km after first 2 km)
            if distance_km <= 2:
                distance_fee = 0
            else:
                distance_fee = (distance_km - 2) * 2.0
            
            # Apply weather factor (higher fees in bad weather)
            weather_adjustment = distance_fee * (weather_factor - 1.0)
            
            # Apply time factor (peak hours, etc.)
            time_adjustment = distance_fee * (time_factor - 1.0)
            
            # Order value discount (free delivery for orders > threshold)
            if order_value >= settings.free_delivery_threshold:
                value_discount = base_fee + distance_fee + weather_adjustment + time_adjustment
            else:
                value_discount = 0
            
            # Total fee
            total_fee = base_fee + distance_fee + weather_adjustment + time_adjustment - value_discount
            
            # Ensure minimum fee
            total_fee = max(total_fee, 2.0)
            
            return {
                "base_fee": base_fee,
                "distance_fee": distance_fee,
                "weather_adjustment": round(weather_adjustment, 2),
                "time_adjustment": round(time_adjustment, 2),
                "value_discount": value_discount,
                "total_fee": round(total_fee, 2),
                "distance_km": distance_km,
                "order_value": order_value,
                "weather_factor": weather_factor,
                "time_factor": time_factor
            }
            
        except Exception as e:
            logger.error(f"Error calculating delivery fee: {e}")
            return {
                "base_fee": 5.0,
                "distance_fee": 0,
                "weather_adjustment": 0,
                "time_adjustment": 0,
                "value_discount": 0,
                "total_fee": 5.0,
                "distance_km": distance_km,
                "order_value": order_value,
                "error": str(e)
            }
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        حساب المسافة بين نقطتين باستخدام صيغة هافرساين
        """
        try:
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Earth radius in kilometers
            r = 6371
            
            return c * r
            
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return 0.0
    
    async def find_available_captain(self, location: str, required_rating: float = 0.0) -> Optional[Captain]:
        """
        Find available captain near the location with rating filter
        البحث عن كابتن متاح قريب من الموقع مع فلتر التقييم
        """
        try:
            query = select(Captain).where(
                Captain.available == True,
                Captain.performance >= required_rating
            ).order_by(Captain.performance.desc())
            
            result = await self.db.execute(query)
            captain = result.scalar_one_or_none()
            
            return captain
            
        except Exception as e:
            logger.error(f"Error finding available captain: {e}")
            return None
    
    async def estimate_delivery_time(self, distance_km: float, traffic_factor: float = 1.0, 
                                   weather_factor: float = 1.0) -> int:
        """
        Estimate delivery time in minutes with advanced factors
        تقدير وقت التوصيل بالدقائق مع عوامل متقدمة
        """
        try:
            # Base time: 10 minutes for pickup + 2 minutes per km
            base_time = 10 + (distance_km * 2)
            
            # Apply traffic factor
            traffic_time = base_time * traffic_factor
            
            # Apply weather factor
            weather_time = traffic_time * weather_factor
            
            # Round to nearest 5 minutes
            estimated_time = round(weather_time / 5) * 5
            
            return max(estimated_time, 15)  # Minimum 15 minutes
            
        except Exception as e:
            logger.error(f"Error estimating delivery time: {e}")
            return 30  # Default 30 minutes
    
    async def get_delivery_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get delivery analytics for AI insights
        الحصول على تحليلات التوصيل لرؤى الذكاء الاصطناعي
        """
        try:
            # Get orders from last N days
            query = select(Order).where(
                Order.time_created >= func.date(func.now() - func.interval(f'{days} days'))
            )
            
            result = await self.db.execute(query)
            orders = result.scalars().all()
            
            if not orders:
                return {"message": "No orders found", "analytics": {}}
            
            # Calculate analytics
            total_orders = len(orders)
            total_revenue = sum(float(order.total_price_customer) for order in orders if order.total_price_customer)
            avg_delivery_fee = sum(float(order.delivery_fee) for order in orders if order.delivery_fee) / total_orders
            avg_order_value = total_revenue / total_orders
            
            # Status distribution
            status_counts = {}
            for order in orders:
                status_counts[order.status] = status_counts.get(order.status, 0) + 1
            
            return {
                "period_days": days,
                "total_orders": total_orders,
                "total_revenue": round(total_revenue, 2),
                "avg_delivery_fee": round(avg_delivery_fee, 2),
                "avg_order_value": round(avg_order_value, 2),
                "status_distribution": status_counts,
                "success_rate": (status_counts.get("delivered", 0) / total_orders) * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting delivery analytics: {e}")
            return {"error": str(e)}
    
    async def optimize_route(self, orders: List[Order]) -> List[Order]:
        """
        Optimize delivery route using AI algorithms (placeholder for future implementation)
        تحسين مسار التوصيل باستخدام خوارزميات الذكاء الاصطناعي
        """
        try:
            # This is a placeholder for future AI route optimization
            # For now, return orders sorted by creation time
            return sorted(orders, key=lambda x: x.time_created)
            
        except Exception as e:
            logger.error(f"Error optimizing route: {e}")
            return orders 