from . import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text
from sqlalchemy.sql import func


class Note(Base):
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String(20), nullable=False)  # 'order' | 'customer' | 'restaurant' | 'captain' | 'issue'
    reference_id = Column(Integer, nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)


