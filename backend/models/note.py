from . import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.sql import func


class Note(Base):
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True, index=True)
    note_type = Column(
        PGEnum(
            'customer', 'restaurant', 'captain', 'order', 'issue', 'call',
            name='note_type_enum',
            create_type=False,
        ),
        nullable=False,
    )
    target_type = Column(
        PGEnum(
            'customer', 'restaurant', 'captain', 'order', 'issue', 'call',
            name='note_target_enum',
            create_type=False,
        ),
        nullable=False,
    )
    reference_id = Column(Integer, nullable=False)
    issue_id = Column(Integer, nullable=True)
    note_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    source = Column(String(20), default='employee')  # 'employee' | 'ai'


