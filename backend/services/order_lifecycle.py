"""
Order lifecycle management service
خدمة إدارة دورة حياة الطلب
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from backend.models.orders import Order, OrderStageDuration
from backend.models.enums import OrderStatusEnum
from backend.config import settings


class OrderLifecycleService:
    """Service for managing order lifecycle and duration calculations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order_stage(self, order_id: int, stage_name: str, 
                               start_time: Optional[datetime] = None) -> OrderStageDuration:
        """Create a new order stage"""
        if start_time is None:
            start_time = datetime.now()
            
        stage = OrderStageDuration(
            order_id=order_id,
            stage_name=stage_name,
            stage_start_time=start_time,
            stage_status="active"
        )
        
        self.db.add(stage)
        await self.db.commit()
        await self.db.refresh(stage)
        return stage
    
    async def complete_order_stage(self, order_id: int, stage_name: str, 
                                 end_time: Optional[datetime] = None) -> OrderStageDuration:
        """Complete an order stage and calculate duration"""
        if end_time is None:
            end_time = datetime.now()
            
        # Find the active stage
        query = select(OrderStageDuration).where(
            and_(
                OrderStageDuration.order_id == order_id,
                OrderStageDuration.stage_name == stage_name,
                OrderStageDuration.stage_status == "active"
            )
        )
        
        result = await self.db.execute(query)
        stage = result.scalar_one_or_none()
        
        if stage:
            stage.stage_end_time = end_time
            stage.duration = end_time - stage.stage_start_time
            stage.stage_status = "completed"
            stage.updated_at = datetime.now()
            
            await self.db.commit()
            await self.db.refresh(stage)
            
        return stage
    
    async def get_order_durations(self, order_id: int) -> Dict[str, Any]:
        """Get all stage durations for an order"""
        query = select(OrderStageDuration).where(
            OrderStageDuration.order_id == order_id
        ).order_by(OrderStageDuration.stage_start_time)
        
        result = await self.db.execute(query)
        stages = result.scalars().all()
        
        durations = {}
        total_duration = timedelta()
        longest_stage = None
        longest_duration = timedelta()
        
        for stage in stages:
            if stage.duration:
                durations[stage.stage_name] = {
                    "duration": stage.duration,
                    "start_time": stage.stage_start_time,
                    "end_time": stage.stage_end_time,
                    "status": stage.stage_status
                }
                total_duration += stage.duration
                
                if stage.duration > longest_duration:
                    longest_duration = stage.duration
                    longest_stage = stage.stage_name
        
        return {
            "stages": durations,
            "total_duration": total_duration,
            "longest_stage": longest_stage,
            "longest_duration": longest_duration
        }
    
    async def calculate_processing_time(self, order_id: int) -> Dict[str, Any]:
        """Calculate processing time and related metrics"""
        # Get order with stage durations
        query = select(Order).options(
            selectinload(Order.stage_durations)
        ).where(Order.order_id == order_id)
        
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            return {}
        
        durations = await self.get_order_durations(order_id)
        
        # Calculate processing time (time_out_for_delivery - time_created)
        out_for_delivery_stage = durations["stages"].get("out_for_delivery")
        processing_time = None
        if out_for_delivery_stage and order.time_created:
            processing_time = out_for_delivery_stage["start_time"] - order.time_created
        
        # Calculate total processing duration (time_delivered - time_created)
        delivered_stage = durations["stages"].get("delivered")
        total_processing_duration = None
        if delivered_stage and order.time_created:
            total_processing_duration = delivered_stage["start_time"] - order.time_created
        
        return {
            "order_id": order_id,
            "time_created": order.time_created,
            "processing_time": processing_time,
            "total_processing_duration": total_processing_duration,
            "durations": durations,
            "longest_phase": durations.get("longest_stage"),
            "longest_phase_duration": durations.get("longest_duration")
        }
    
    async def validate_timestamps(self, order_id: int) -> Dict[str, bool]:
        """Validate logical order of timestamps"""
        durations = await self.get_order_durations(order_id)
        stages = durations["stages"]
        
        validations = {
            "pending_before_accept": True,
            "accept_before_preparing": True,
            "preparing_before_delivery": True,
            "delivery_before_delivered": True
        }
        
        # Check pending -> accept
        if "pending" in stages and "accepted" in stages:
            if stages["pending"]["end_time"] > stages["accepted"]["start_time"]:
                validations["pending_before_accept"] = False
        
        # Check accept -> preparing
        if "accepted" in stages and "preparing" in stages:
            if stages["accepted"]["end_time"] > stages["preparing"]["start_time"]:
                validations["accept_before_preparing"] = False
        
        # Check preparing -> out_for_delivery
        if "preparing" in stages and "out_for_delivery" in stages:
            if stages["preparing"]["end_time"] > stages["out_for_delivery"]["start_time"]:
                validations["preparing_before_delivery"] = False
        
        # Check out_for_delivery -> delivered
        if "out_for_delivery" in stages and "delivered" in stages:
            if stages["out_for_delivery"]["end_time"] > stages["delivered"]["start_time"]:
                validations["delivery_before_delivered"] = False
        
        return validations
    
    async def update_order_status(self, order_id: int, new_status: OrderStatusEnum) -> Order:
        """Update order status and handle stage transitions"""
        query = select(Order).where(Order.order_id == order_id)
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        old_status = order.status
        order.status = new_status
        
        # Handle stage transitions
        if new_status == OrderStatusEnum.ACCEPTED and old_status == OrderStatusEnum.PENDING:
            await self.complete_order_stage(order_id, "pending")
            await self.create_order_stage(order_id, "accepted")
            
        elif new_status == OrderStatusEnum.PREPARING and old_status == OrderStatusEnum.ACCEPTED:
            await self.complete_order_stage(order_id, "accepted")
            await self.create_order_stage(order_id, "preparing")
            
        elif new_status == OrderStatusEnum.OUT_FOR_DELIVERY and old_status == OrderStatusEnum.PREPARING:
            await self.complete_order_stage(order_id, "preparing")
            await self.create_order_stage(order_id, "out_for_delivery")
            
        elif new_status == OrderStatusEnum.DELIVERED and old_status == OrderStatusEnum.OUT_FOR_DELIVERY:
            await self.complete_order_stage(order_id, "out_for_delivery")
            await self.create_order_stage(order_id, "delivered")
        
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def get_orders_with_durations(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get orders with their duration calculations"""
        query = select(Order).options(
            selectinload(Order.stage_durations)
        ).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        orders_with_durations = []
        for order in orders:
            durations = await self.get_order_durations(order.order_id)
            processing_metrics = await self.calculate_processing_time(order.order_id)
            
            orders_with_durations.append({
                "order": order,
                "durations": durations,
                "processing_metrics": processing_metrics
            })
        
        return orders_with_durations 