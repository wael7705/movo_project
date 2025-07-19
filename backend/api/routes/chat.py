"""
Chat API routes with async support
مسارات API للدردشة مع دعم غير متزامن
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from backend.database.database import get_db
from backend.services.chat_service import ChatService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class MessageCreate(BaseModel):
    order_id: int
    sender_type: str
    sender_id: int
    message: str
    ai_enhanced: bool = False


@router.post("/messages", response_model=Dict[str, Any])
async def send_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Send a new chat message"""
    try:
        chat_service = ChatService(db)
        result = await chat_service.send_message(
            order_id=message_data.order_id,
            sender_type=message_data.sender_type,
            sender_id=message_data.sender_id,
            message=message_data.message,
            ai_enhanced=message_data.ai_enhanced
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/messages/{order_id}", response_model=List[Dict[str, Any]])
async def get_messages(
    order_id: int,
    limit: int = 50,
    include_ai_insights: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get chat messages for an order"""
    try:
        chat_service = ChatService(db)
        messages = await chat_service.get_messages(
            order_id=order_id,
            limit=limit,
            include_ai_insights=include_ai_insights
        )
        
        return messages
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/messages/{message_id}/read", response_model=Dict[str, Any])
async def mark_message_read(
    message_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark a message as read"""
    try:
        chat_service = ChatService(db)
        result = await chat_service.mark_as_read(message_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/unread/{order_id}", response_model=Dict[str, Any])
async def get_unread_count(
    order_id: int,
    user_type: str,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread messages for a user"""
    try:
        chat_service = ChatService(db)
        count = await chat_service.get_unread_count(
            order_id=order_id,
            user_type=user_type,
            user_id=user_id
        )
        
        return {
            "order_id": order_id,
            "user_type": user_type,
            "user_id": user_id,
            "unread_count": count
        }
        
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/summary/{order_id}", response_model=Dict[str, Any])
async def get_chat_summary(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chat summary for an order"""
    try:
        chat_service = ChatService(db)
        summary = await chat_service.get_order_chat_summary(order_id)
        
        if "error" in summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary["error"]
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 