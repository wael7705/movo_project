"""
Customers API routes with async support
مسارات API للعملاء مع دعم غير متزامن
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from ...database.database import get_db  # استيراد نسبي لضمان العمل من الجذر
from ...models import Customer, CustomerAddress
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class CustomerCreate(BaseModel):
    name: str
    phone: str
    latitude: float
    longitude: float
    membership_type: str = 'normal'


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    membership_type: Optional[str] = None


@router.post("/", response_model=Dict[str, Any])
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer"""
    try:
        customer = Customer(
            name=customer_data.name,
            phone=customer_data.phone,
            latitude=customer_data.latitude,
            longitude=customer_data.longitude,
            membership_type=customer_data.membership_type
        )
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "phone": customer.phone,
            "latitude": float(customer.latitude) if customer.latitude is not None and not hasattr(customer.latitude, '__clause_element__') else None,
            "longitude": float(customer.longitude) if customer.longitude is not None and not hasattr(customer.longitude, '__clause_element__') else None,
            "membership_type": customer.membership_type
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=List[Dict[str, Any]])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all customers with pagination"""
    try:
        from sqlalchemy import select
        query = select(Customer).offset(skip).limit(limit)
        result = await db.execute(query)
        customers = result.scalars().all()
        
        def safe_float(val):
            from sqlalchemy.orm.attributes import InstrumentedAttribute
            if isinstance(val, (float, int)):
                return float(val)
            if val is None or isinstance(val, InstrumentedAttribute):
                return None
            try:
                return float(val)
            except Exception:
                return None
        
        return [
            {
                "customer_id": customer.customer_id,
                "name": customer.name,
                "phone": customer.phone,
                "latitude": safe_float(customer.latitude),
                "longitude": safe_float(customer.longitude),
                "membership_type": customer.membership_type
            }
            for customer in customers
        ]
        
    except Exception as e:
        logger.error(f"Error getting customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{customer_id}", response_model=Dict[str, Any])
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific customer by ID"""
    try:
        from sqlalchemy import select
        query = select(Customer).where(Customer.customer_id == customer_id)
        result = await db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        def safe_float(val):
            from sqlalchemy.orm.attributes import InstrumentedAttribute
            if isinstance(val, (float, int)):
                return float(val)
            if val is None or isinstance(val, InstrumentedAttribute):
                return None
            try:
                return float(val)
            except Exception:
                return None
        
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "phone": customer.phone,
            "latitude": safe_float(customer.latitude),
            "longitude": safe_float(customer.longitude),
            "membership_type": customer.membership_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{customer_id}", response_model=Dict[str, Any])
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update customer information"""
    try:
        from sqlalchemy import select
        query = select(Customer).where(Customer.customer_id == customer_id)
        result = await db.execute(query)
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        # Update fields if provided
        for field, value in customer_update.dict(exclude_unset=True).items():
            setattr(customer, field, value)
        await db.commit()
        await db.refresh(customer)
        def safe_float(val):
            from sqlalchemy.orm.attributes import InstrumentedAttribute
            if isinstance(val, (float, int)):
                return float(val)
            if val is None or isinstance(val, InstrumentedAttribute):
                return None
            try:
                return float(val)
            except Exception:
                return None
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "phone": customer.phone,
            "latitude": safe_float(customer.latitude),
            "longitude": safe_float(customer.longitude),
            "membership_type": customer.membership_type
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 