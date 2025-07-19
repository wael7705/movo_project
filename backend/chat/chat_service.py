"""
Real-time chat service using WebSocket
خدمة الدردشة الفورية باستخدام WebSocket
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Remove the problematic import
# from models.employees import Employee

logging.basicConfig(filename='chat_errors.log', level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s:%(message)s')

@dataclass
class ChatMessage:
    """Chat message data structure"""
    sender_id: int
    sender_name: str
    department: str
    content: str
    timestamp: datetime
    message_type: str = "text"  # text, system, notification


@dataclass
class ChatUser:
    """Chat user data structure"""
    user_id: int
    name: str
    department: str
    websocket: WebSocket
    is_online: bool = True


class ChatService:
    """Real-time chat service"""
    
    def __init__(self):
        self.active_connections: Dict[int, ChatUser] = {}
        self.department_rooms: Dict[str, Set[int]] = {}
        self.message_history: List[ChatMessage] = []
        self.max_history = 1000  # Keep last 1000 messages
    
    async def connect(self, websocket: WebSocket, user_id: int, 
                     name: str, department: str) -> ChatUser:
        """Connect a user to the chat"""
        await websocket.accept()
        
        user = ChatUser(
            user_id=user_id,
            name=name,
            department=department,
            websocket=websocket
        )
        
        self.active_connections[user_id] = user
        
        # Add to department room
        if department not in self.department_rooms:
            self.department_rooms[department] = set()
        self.department_rooms[department].add(user_id)
        
        # Send welcome message
        welcome_msg = ChatMessage(
            sender_id=0,
            sender_name="System",
            department="system",
            content=f"مرحباً {name}! تم الاتصال بنجاح.",
            timestamp=datetime.now(),
            message_type="system"
        )
        
        await self.send_personal_message(welcome_msg, user_id)
        
        # Notify others in department
        await self.broadcast_to_department(
            ChatMessage(
                sender_id=0,
                sender_name="System",
                department="system",
                content=f"{name} انضم إلى الدردشة",
                timestamp=datetime.now(),
                message_type="notification"
            ),
            department,
            exclude_user_id=user_id
        )
        
        return user
    
    async def disconnect(self, user_id: int):
        """Disconnect a user from the chat"""
        if user_id in self.active_connections:
            user = self.active_connections[user_id]
            user.is_online = False
            
            # Remove from department room
            if user.department in self.department_rooms:
                self.department_rooms[user.department].discard(user_id)
            
            # Notify others in department
            await self.broadcast_to_department(
                ChatMessage(
                    sender_id=0,
                    sender_name="System",
                    department="system",
                    content=f"{user.name} غادر الدردشة",
                    timestamp=datetime.now(),
                    message_type="notification"
                ),
                user.department
            )
            
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: ChatMessage, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            user = self.active_connections[user_id]
            try:
                await user.websocket.send_text(json.dumps(asdict(message), default=str))
            except Exception as e:
                logging.error(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast_to_department(self, message: ChatMessage, department: str, 
                                    exclude_user_id: Optional[int] = None):
        """Broadcast a message to all users in a department"""
        if department in self.department_rooms:
            for user_id in self.department_rooms[department]:
                if user_id != exclude_user_id:
                    await self.send_personal_message(message, user_id)
    
    async def broadcast_to_all(self, message: ChatMessage, exclude_user_id: Optional[int] = None):
        """Broadcast a message to all connected users"""
        for user_id in self.active_connections:
            if user_id != exclude_user_id:
                await self.send_personal_message(message, user_id)
    
    async def handle_message(self, user_id: int, content: str, message_type: str = "text"):
        """Handle incoming message from a user"""
        if user_id not in self.active_connections:
            return
        
        user = self.active_connections[user_id]
        
        # Create message
        message = ChatMessage(
            sender_id=user_id,
            sender_name=user.name,
            department=user.department,
            content=content,
            timestamp=datetime.now(),
            message_type=message_type
        )
        
        # Add to history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        # Broadcast to department
        await self.broadcast_to_department(message, user.department)
    
    async def get_message_history(self, department: Optional[str] = None, 
                                limit: int = 50) -> List[Dict]:
        """Get message history"""
        history = self.message_history
        
        # Filter by department if specified
        if department:
            history = [msg for msg in history if msg.department == department]
        
        # Return last N messages
        recent_messages = history[-limit:] if len(history) > limit else history
        
        return [asdict(msg) for msg in recent_messages]
    
    async def get_online_users(self, department: Optional[str] = None) -> List[Dict]:
        """Get list of online users"""
        users = []
        
        for user in self.active_connections.values():
            if not department or user.department == department:
                users.append({
                    "user_id": user.user_id,
                    "name": user.name,
                    "department": user.department,
                    "is_online": user.is_online
                })
        
        return users
    
    async def get_department_stats(self) -> Dict[str, int]:
        """Get statistics by department"""
        stats = {}
        
        for user in self.active_connections.values():
            dept = user.department
            stats[dept] = stats.get(dept, 0) + 1
        
        return stats


# Global chat service instance
chat_service = ChatService()


class ChatManager:
    """Chat manager for handling WebSocket connections"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_service = chat_service
    
    async def handle_websocket(self, websocket: WebSocket, user_id: int):
        """Handle WebSocket connection for a user"""
        try:
            # Get user details from database - simplified for now
            # from sqlalchemy import select
            # query = select(Employee).where(Employee.employee_id == user_id)
            # result = await self.db.execute(query)
            # employee = result.scalar_one_or_none()
            
            # For now, use mock employee data
            employee_name = f"User_{user_id}"
            employee_department = "general"
            
            # Connect user to chat
            user = await self.chat_service.connect(
                websocket=websocket,
                user_id=user_id,
                name=employee_name,
                department=employee_department
            )
            
            # Handle messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    content = message_data.get("content", "")
                    message_type = message_data.get("type", "text")
                    
                    if content.strip():
                        await self.chat_service.handle_message(
                            user_id=user_id,
                            content=content,
                            message_type=message_type
                        )
                
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logging.error(f"Error handling message: {e}")
                    # Send error message to user
                    error_msg = ChatMessage(
                        sender_id=0,
                        sender_name="System",
                        department="system",
                        content="حدث خطأ في معالجة الرسالة",
                        timestamp=datetime.now(),
                        message_type="system"
                    )
                    await self.chat_service.send_personal_message(error_msg, user_id)
        
        except WebSocketDisconnect:
            pass
        finally:
            await self.chat_service.disconnect(user_id)
    
    async def send_system_message(self, content: str, department: Optional[str] = None):
        """Send a system message"""
        message = ChatMessage(
            sender_id=0,
            sender_name="System",
            department="system",
            content=content,
            timestamp=datetime.now(),
            message_type="system"
        )
        
        if department:
            await self.chat_service.broadcast_to_department(message, department)
        else:
            await self.chat_service.broadcast_to_all(message)
    
    async def send_notification(self, content: str, department: str):
        """Send a notification to a department"""
        message = ChatMessage(
            sender_id=0,
            sender_name="System",
            department="system",
            content=content,
            timestamp=datetime.now(),
            message_type="notification"
        )
        
        await self.chat_service.broadcast_to_department(message, department) 