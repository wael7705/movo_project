from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from backend.database.config import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, index=True)
    sender_type = Column(String(32), nullable=False)
    sender_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False) 