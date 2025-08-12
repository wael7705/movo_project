"""
Orders API routes with async support
مسارات API للطلبات مع دعم غير متزامن
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from backend.database.database import get_db
from backend.models import Order, Note
from backend.services.delivery_service import DeliveryService
from pydantic import BaseModel
import logging
from backend.models.enums import OrderStatusEnum

logger = logging.getLogger(__name__)

router = APIRouter()


class OrderCreate(BaseModel):
    customer_id: int
    restaurant_id: int
    items: List[Dict[str, Any]]
    delivery_address: str
    delivery_lat: float
    delivery_lon: float


class OrderUpdate(BaseModel):
    status: str
    captain_id: int = None


@router.post("/", response_model=Dict[str, Any])
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new order with delivery fee calculation"""
    try:
        delivery_service = DeliveryService(db)
        
        # Calculate delivery fee
        distance = delivery_service.calculate_distance(
            lat1=24.7136, lon1=46.6753,  # Default restaurant location (Riyadh)
            lat2=order_data.delivery_lat,
            lon2=order_data.delivery_lon
        )
        
        fee_result = await delivery_service.calculate_delivery_fee(
            distance_km=distance,
            order_value=sum(item.get('price', 0) for item in order_data.items)
        )
        
        # Create order
        order = Order(
            customer_id=order_data.customer_id,
            restaurant_id=order_data.restaurant_id,
            delivery_fee=fee_result['total_fee'],
            total_price_customer=sum(item.get('price', 0) for item in order_data.items) + fee_result['total_fee'],
            status="pending"
        )
        
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        return {
            "order_id": order.order_id,
            "delivery_fee": fee_result,
            "total_amount": order.total_price_customer,
            "estimated_time": await delivery_service.estimate_delivery_time(distance)
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# 1. تصفية الطلبات حسب الحالة
@router.get("/", response_model=List[Dict[str, Any]])
async def get_orders(
    order_status: str = None,  # <-- غيرت الاسم هنا
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all orders with optional status filter and pagination"""
    try:
        from sqlalchemy import select
        query = select(Order)
        if order_status:
            query = query.where(Order.status == order_status)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        orders = result.scalars().all()
        return [
            {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "restaurant_id": order.restaurant_id,
                "status": order.status,
                "total_price_customer": order.total_price_customer,
                "delivery_fee": order.delivery_fee,
                "created_at": order.created_at.isoformat() if getattr(order, 'created_at', None) else None
            }
            for order in orders
        ]
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting orders: {e}")
        from fastapi import status as fastapi_status
        raise HTTPException(
            status_code=fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{order_id}", response_model=Dict[str, Any])
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific order by ID"""
    try:
        from sqlalchemy import select
        query = select(Order).where(Order.order_id == order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "restaurant_id": order.restaurant_id,
            "status": order.status,
            "total_price_customer": order.total_price_customer,
            "delivery_fee": order.delivery_fee,
            "captain_id": order.captain_id,
            "created_at": order.created_at.isoformat() if getattr(order, 'created_at', None) else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{order_id}", response_model=Dict[str, Any])
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update order status and assign captain"""
    try:
        from sqlalchemy import select
        query = select(Order).where(Order.order_id == order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order.status = order_update.status
        if order_update.captain_id:
            order.captain_id = order_update.captain_id
        
        await db.commit()
        await db.refresh(order)
        
        return {
            "order_id": order.order_id,
            "status": order.status,
            "captain_id": order.captain_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 

# 2. Endpoints للملاحظات
class NoteCreate(BaseModel):
    note_text: str

@router.get("/{order_id}/notes", response_model=List[Dict[str, Any]])
async def get_order_notes(order_id: int, db: AsyncSession = Depends(get_db)):
    """Get notes for a specific order"""
    try:
        from sqlalchemy import select
        query = select(Note).where(Note.target_type == "order", Note.reference_id == order_id)
        result = await db.execute(query)
        notes = result.scalars().all()
        return [
            {
                "note_id": note.note_id,
                "note_text": note.note_text,
                "created_at": note.created_at.isoformat() if note.created_at else None
            }
            for note in notes
        ]
    except Exception as e:
        logger.error(f"Error getting notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{order_id}/notes", response_model=Dict[str, Any])
async def add_note(order_id: int, note: NoteCreate, db: AsyncSession = Depends(get_db)):
    """Add a note to an order"""
    try:
        new_note = Note(
            note_type="order",
            target_type="order",
            reference_id=order_id,
            note_text=note.note_text
        )
        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)
        return {
            "note_id": new_note.note_id,
            "note_text": new_note.note_text,
            "created_at": new_note.created_at.isoformat() if new_note.created_at else None
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error adding note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# 3. Endpoint لتعديل العنوان
class AddressUpdate(BaseModel):
    new_address: str

@router.patch("/{order_id}/address", response_model=Dict[str, Any])
async def update_order_address(order_id: int, address_update: AddressUpdate, db: AsyncSession = Depends(get_db)):
    """Update order address"""
    try:
        from sqlalchemy import select
        query = select(Order).where(Order.order_id == order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        order.delivery_address = address_update.new_address
        await db.commit()
        await db.refresh(order)
        return {
            "order_id": order.order_id,
            "delivery_address": order.delivery_address
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating address: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# 4. WebSocket لتحديثات لحظية
@router.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # يمكنك هنا إرسال إشعار عند تحديث الطلبات
            await websocket.send_text("order_updated")
    except WebSocketDisconnect:
        pass 