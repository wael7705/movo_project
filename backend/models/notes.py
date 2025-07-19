"""
Note models
نماذج الملاحظات
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.config import Base
from .enums import NoteTypeEnum, NoteTargetEnum


class Note(Base):
    """Note model"""
    __tablename__ = "notes"
    
    note_id = Column(Integer, primary_key=True, index=True)
    note_type = Column(String(20), nullable=False)  # customer, restaurant, captain, order, issue
    target_type = Column(String(20), nullable=False)  # customer, restaurant, captain, order, issue
    reference_id = Column(Integer, nullable=False)  # Unified reference ID for all entity types
    issue_id = Column(Integer, ForeignKey("issues.issue_id", ondelete="SET NULL"))
    note_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())
    
    # Relationships
    issue = relationship("Issue", back_populates="notes")
    order = relationship("Order", back_populates="notes") 