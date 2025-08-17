"""
Captains API routes with async support
مسارات API للكباتن مع دعم غير متزامن
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from ...database.database import get_db  # استيراد نسبي لضمان العمل من الجذر
from ...models import Captain
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class CaptainCreate(BaseModel):
    name: str
    phone: str
    vehicle_type: str
    vehicle_number: str = None
    current_lat: float = 24.7136
    current_lon: float = 46.6753


class CaptainUpdate(BaseModel):
    name: str = None
    phone: str = None
    available: bool = None
    current_lat: float = None
    current_lon: float = None
    performance: float = None


@router.post("/", response_model=Dict[str, Any])
async def create_captain(
    captain_data: CaptainCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new captain"""
    try:
        captain = Captain(
            name=captain_data.name,
            phone=captain_data.phone,
            vehicle_type=captain_data.vehicle_type,
            available=True,
            performance=5.0
        )
        
        db.add(captain)
        await db.commit()
        await db.refresh(captain)
        
        return {
            "captain_id": captain.captain_id,
            "name": captain.name,
            "phone": captain.phone,
            "vehicle_type": captain.vehicle_type,
            "available": captain.available,
            "performance": captain.performance
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating captain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=List[Dict[str, Any]])
async def get_captains(
    available_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all captains with optional availability filter"""
    try:
        from sqlalchemy import select
        query = select(Captain)
        
        if available_only:
            query = query.where(Captain.available == True)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        captains = result.scalars().all()
        
        return [
            {
                "captain_id": captain.captain_id,
                "name": captain.name,
                "phone": captain.phone,
                "vehicle_type": captain.vehicle_type,
                "available": captain.available,
                "performance": captain.performance,
                "orders_delivered": captain.orders_delivered
            }
            for captain in captains
        ]
        
    except Exception as e:
        logger.error(f"Error getting captains: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{captain_id}", response_model=Dict[str, Any])
async def get_captain(
    captain_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific captain by ID"""
    try:
        from sqlalchemy import select
        query = select(Captain).where(Captain.captain_id == captain_id)
        result = await db.execute(query)
        captain = result.scalar_one_or_none()
        
        if not captain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Captain not found"
            )
        
        return {
            "captain_id": captain.captain_id,
            "name": captain.name,
            "phone": captain.phone,
            "vehicle_type": captain.vehicle_type,
            "available": captain.available,
            "performance": captain.performance,
            "orders_delivered": captain.orders_delivered
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting captain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{captain_id}", response_model=Dict[str, Any])
async def update_captain(
    captain_id: int,
    captain_update: CaptainUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update captain information"""
    try:
        from sqlalchemy import select
        query = select(Captain).where(Captain.captain_id == captain_id)
        result = await db.execute(query)
        captain = result.scalar_one_or_none()
        
        if not captain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Captain not found"
            )
        
        # Update fields if provided
        if captain_update.name is not None:
            captain.name = captain_update.name
        if captain_update.phone is not None:
            captain.phone = captain_update.phone
        if captain_update.available is not None:
            captain.available = captain_update.available
        if captain_update.performance is not None:
            captain.performance = captain_update.performance
        
        await db.commit()
        await db.refresh(captain)
        
        return {
            "captain_id": captain.captain_id,
            "name": captain.name,
            "phone": captain.phone,
            "available": captain.available,
            "performance": captain.performance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating captain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 