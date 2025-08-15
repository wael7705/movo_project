"""
Analytics API routes with async support
مسارات API للتحليلات مع دعم غير متزامن
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from ...database.database import get_db  # استيراد نسبي لضمان العمل من الجذر
from ...services.delivery_service import DeliveryService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/delivery", response_model=Dict[str, Any])
async def get_delivery_analytics(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get delivery analytics for AI insights"""
    try:
        delivery_service = DeliveryService(db)
        analytics = await delivery_service.get_delivery_analytics(days=days)
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics["error"]
            )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting delivery analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    db: AsyncSession = Depends(get_db)
):
    """Get overall system performance metrics"""
    try:
        from sqlalchemy import select, func
        from ...models import Order, Captain, Restaurant
        
        # Get basic counts
        result = await db.execute(select(func.count(Order.order_id)))
        total_orders = result.scalar() or 0
        
        result = await db.execute(select(func.count(Captain.captain_id)))
        total_captains = result.scalar() or 0
        
        result = await db.execute(select(func.count(Restaurant.restaurant_id)))
        total_restaurants = result.scalar() or 0
        
        # Get delivered orders
        result = await db.execute(
            select(func.count(Order.order_id)).where(Order.status == 'delivered')
        )
        delivered_orders = result.scalar() or 0
        
        # Calculate success rate
        success_rate = (delivered_orders / total_orders * 100) if total_orders > 0 else 0
        
        # Get average delivery fee
        result = await db.execute(
            select(func.avg(Order.delivery_fee)).where(Order.delivery_fee.isnot(None))
        )
        avg_delivery_fee = result.scalar() or 0
        
        return {
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "success_rate": round(success_rate, 2),
            "total_captains": total_captains,
            "total_restaurants": total_restaurants,
            "avg_delivery_fee": round(float(avg_delivery_fee), 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/captains/performance", response_model=List[Dict[str, Any]])
async def get_captain_performance(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get top performing captains"""
    try:
        from sqlalchemy import select
        from ...models import Captain
        
        query = select(Captain).order_by(
            Captain.performance.desc(),
            Captain.orders_delivered.desc()
        ).limit(limit)
        
        result = await db.execute(query)
        captains = result.scalars().all()
        
        return [
            {
                "captain_id": captain.captain_id,
                "name": captain.name,
                "performance": captain.performance,
                "orders_delivered": captain.orders_delivered,
                "available": captain.available
            }
            for captain in captains
        ]
        
    except Exception as e:
        logger.error(f"Error getting captain performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/restaurants/activity", response_model=List[Dict[str, Any]])
async def get_restaurant_activity(
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant activity status"""
    try:
        from sqlalchemy import select, func
        from ...models import Restaurant, Order
        
        # Get restaurants with order counts
        query = select(
            Restaurant.restaurant_id,
            Restaurant.name,
            Restaurant.status,
            Restaurant.availability,
            func.count(Order.order_id).label('order_count')
        ).outerjoin(Order, Restaurant.restaurant_id == Order.restaurant_id).group_by(
            Restaurant.restaurant_id,
            Restaurant.name,
            Restaurant.status,
            Restaurant.availability
        )
        
        result = await db.execute(query)
        restaurants = result.all()
        
        return [
            {
                "restaurant_id": restaurant.restaurant_id,
                "name": restaurant.name,
                "status": restaurant.status,
                "availability": restaurant.availability,
                "order_count": restaurant.order_count
            }
            for restaurant in restaurants
        ]
        
    except Exception as e:
        logger.error(f"Error getting restaurant activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 