"""
Advanced chat service with AI support for MOVO delivery platform
خدمة الدردشة المتقدمة مع دعم الذكاء الاصطناعي لمنصة MOVO للتوصيل
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models import ChatMessage, Order
from ..config import settings  # استيراد نسبي لضمان العمل من الجذر
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Advanced service for chat-related operations with AI support"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def send_message(self, order_id: int, sender_type: str, sender_id: int, 
                          message: str, ai_enhanced: bool = False) -> Dict[str, Any]:
        """
        Send a new chat message with optional AI enhancement
        إرسال رسالة دردشة جديدة مع تحسين اختياري بالذكاء الاصطناعي
        """
        try:
            # AI enhancement (placeholder for future implementation)
            if ai_enhanced:
                message = await self._enhance_message_with_ai(message)
            
            # Create new chat message
            chat_message = ChatMessage(
                order_id=order_id,
                sender_type=sender_type,
                sender_id=sender_id,
                message=message,
                is_read=False
            )
            
            self.db.add(chat_message)
            await self.db.commit()
            await self.db.refresh(chat_message)
            
            return {
                "message_id": chat_message.id,
                "order_id": chat_message.order_id,
                "sender_type": chat_message.sender_type,
                "sender_id": chat_message.sender_id,
                "message": chat_message.message,
                "is_read": chat_message.is_read,
                "ai_enhanced": ai_enhanced,
                "created_at": chat_message.timestamp.isoformat()
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error sending message: {e}")
            return {"error": str(e)}
    
    async def get_messages(self, order_id: int, limit: int = 50, 
                          include_ai_insights: bool = False) -> List[Dict[str, Any]]:
        """
        Get chat messages for an order with optional AI insights
        الحصول على رسائل الدردشة لطلب مع رؤى اختيارية من الذكاء الاصطناعي
        """
        try:
            query = select(ChatMessage).where(
                ChatMessage.order_id == order_id
            ).order_by(ChatMessage.timestamp.desc()).limit(limit)
            
            result = await self.db.execute(query)
            messages = result.scalars().all()
            
            message_list = []
            for msg in messages:
                message_data = {
                    "message_id": msg.id,
                    "order_id": msg.order_id,
                    "sender_type": msg.sender_type,
                    "sender_id": msg.sender_id,
                    "message": msg.message,
                    "is_read": msg.is_read,
                    "created_at": msg.timestamp.isoformat()
                }
                
                # Add AI insights if requested
                if include_ai_insights:
                    message_data["ai_insights"] = await self._get_message_insights(str(msg.message))
                
                message_list.append(message_data)
            
            return message_list
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def mark_as_read(self, message_id: int) -> Dict[str, Any]:
        """
        Mark a message as read
        تحديد رسالة كمقروءة
        """
        try:
            query = select(ChatMessage).where(ChatMessage.id == message_id)
            result = await self.db.execute(query)
            message = result.scalar_one_or_none()
            
            if message:
                message.is_read = True
                await self.db.commit()
                return {"success": True, "message_id": message_id}
            else:
                return {"error": "Message not found"}
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error marking message as read: {e}")
            return {"error": str(e)}
    
    async def get_unread_count(self, order_id: int, user_type: str, user_id: int) -> int:
        """
        Get count of unread messages for a user
        الحصول على عدد الرسائل غير المقروءة للمستخدم
        """
        try:
            query = select(func.count(ChatMessage.id)).where(
                ChatMessage.order_id == order_id,
                ChatMessage.sender_type != user_type,
                ChatMessage.is_read == False
            )
            
            result = await self.db.execute(query)
            count = result.scalar()
            
            return count or 0
            
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0
    
    async def get_order_chat_summary(self, order_id: int) -> Dict[str, Any]:
        """
        Get chat summary for an order with AI analysis
        الحصول على ملخص الدردشة لطلب مع تحليل الذكاء الاصطناعي
        """
        try:
            # Get order details
            query = select(Order).where(Order.order_id == order_id)
            result = await self.db.execute(query)
            order = result.scalar_one_or_none()
            
            if not order:
                return {"error": "Order not found"}
            
            # Get message count
            count_query = select(func.count(ChatMessage.id)).where(ChatMessage.order_id == order_id)
            result = await self.db.execute(count_query)
            message_count = result.scalar() or 0
            
            # Get last message
            last_query = select(ChatMessage).where(
                ChatMessage.order_id == order_id
            ).order_by(ChatMessage.timestamp.desc())
            result = await self.db.execute(last_query)
            last_message = result.scalar_one_or_none()
            
            summary = {
                "order_id": order_id,
                "order_status": order.status,
                "message_count": message_count,
                "last_message": {
                    "sender_type": last_message.sender_type,
                    "message": last_message.message,
                    "created_at": last_message.timestamp.isoformat()
                } if last_message else None
            }
            
            # Add AI analysis if enabled
            if settings.enable_monitoring:
                summary["ai_analysis"] = await self._analyze_chat_sentiment(order_id)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting chat summary: {e}")
            return {"error": str(e)}
    
    async def _enhance_message_with_ai(self, message: str) -> str:
        """
        Enhance message with AI (placeholder for future implementation)
        تحسين الرسالة بالذكاء الاصطناعي
        """
        # Placeholder for AI enhancement
        # In the future, this could include:
        # - Grammar correction
        # - Sentiment analysis
        # - Auto-translation
        # - Smart suggestions
        return message
    
    async def _get_message_insights(self, message: str) -> Dict[str, Any]:
        """
        Get AI insights for a message (placeholder)
        الحصول على رؤى الذكاء الاصطناعي لرسالة
        """
        # Placeholder for AI insights
        return {
            "sentiment": "neutral",
            "confidence": 0.8,
            "suggestions": []
        }
    
    async def _analyze_chat_sentiment(self, order_id: int) -> Dict[str, Any]:
        """
        Analyze chat sentiment for an order (placeholder)
        تحليل مشاعر الدردشة لطلب
        """
        # Placeholder for sentiment analysis
        return {
            "overall_sentiment": "positive",
            "customer_satisfaction": 0.85,
            "response_time_avg": 120,  # seconds
            "escalation_risk": "low"
        } 