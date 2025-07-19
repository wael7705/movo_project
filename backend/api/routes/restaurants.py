"""
Restaurants API routes with async support
مسارات API للمطاعم مع دعم غير متزامن
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from backend.database.database import get_db
from backend.models import Restaurant
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class RestaurantCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    restaurant_location: str = None
    estimated_preparation_time: int
    price_matches: bool = False


class RestaurantUpdate(BaseModel):
    name: str = None
    restaurant_location: str = None
    status: str = None
    availability: str = None
    estimated_preparation_time: int = None
    price_matches: bool = None


@router.post("/", response_model=Dict[str, Any])
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new restaurant"""
    try:
        restaurant = Restaurant(
            name=restaurant_data.name,
            latitude=restaurant_data.latitude,
            longitude=restaurant_data.longitude,
            restaurant_location=restaurant_data.restaurant_location,
            estimated_preparation_time=restaurant_data.estimated_preparation_time,
            price_matches=restaurant_data.price_matches,
            status='offline',
            availability='available'
        )
        
        db.add(restaurant)
        await db.commit()
        await db.refresh(restaurant)
        
        return {
            "restaurant_id": restaurant.restaurant_id,
            "name": restaurant.name,
            "latitude": restaurant.latitude,
            "longitude": restaurant.longitude,
            "restaurant_location": restaurant.restaurant_location,
            "status": restaurant.status,
            "availability": restaurant.availability
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating restaurant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=List[Dict[str, Any]])
async def get_restaurants(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all restaurants with optional active filter"""
    try:
        from sqlalchemy import select
        query = select(Restaurant)
        
        if active_only:
            query = query.where(Restaurant.status == 'online')
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        restaurants = result.scalars().all()
        
        return [
            {
                "restaurant_id": restaurant.restaurant_id,
                "name": restaurant.name,
                "latitude": restaurant.latitude,
                "longitude": restaurant.longitude,
                "restaurant_location": restaurant.restaurant_location,
                "status": restaurant.status,
                "availability": restaurant.availability,
                "estimated_preparation_time": restaurant.estimated_preparation_time
            }
            for restaurant in restaurants
        ]
        
    except Exception as e:
        logger.error(f"Error getting restaurants: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{restaurant_id}", response_model=Dict[str, Any])
async def get_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific restaurant by ID"""
    try:
        from sqlalchemy import select
        query = select(Restaurant).where(Restaurant.restaurant_id == restaurant_id)
        result = await db.execute(query)
        restaurant = result.scalar_one_or_none()
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        return {
            "restaurant_id": restaurant.restaurant_id,
            "name": restaurant.name,
            "latitude": restaurant.latitude,
            "longitude": restaurant.longitude,
            "restaurant_location": restaurant.restaurant_location,
            "status": restaurant.status,
            "availability": restaurant.availability,
            "estimated_preparation_time": restaurant.estimated_preparation_time,
            "price_matches": restaurant.price_matches
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting restaurant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{restaurant_id}", response_model=Dict[str, Any])
async def update_restaurant(
    restaurant_id: int,
    restaurant_update: RestaurantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update restaurant information"""
    try:
        from sqlalchemy import select
        query = select(Restaurant).where(Restaurant.restaurant_id == restaurant_id)
        result = await db.execute(query)
        restaurant = result.scalar_one_or_none()
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Update fields if provided
        if restaurant_update.name is not None:
            restaurant.name = restaurant_update.name
        if restaurant_update.restaurant_location is not None:
            restaurant.restaurant_location = restaurant_update.restaurant_location
        if restaurant_update.status is not None:
            restaurant.status = restaurant_update.status
        if restaurant_update.availability is not None:
            restaurant.availability = restaurant_update.availability
        if restaurant_update.estimated_preparation_time is not None:
            restaurant.estimated_preparation_time = restaurant_update.estimated_preparation_time
        if restaurant_update.price_matches is not None:
            restaurant.price_matches = restaurant_update.price_matches
        
        await db.commit()
        await db.refresh(restaurant)
        
        return {
            "restaurant_id": restaurant.restaurant_id,
            "name": restaurant.name,
            "status": restaurant.status,
            "availability": restaurant.availability
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating restaurant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 