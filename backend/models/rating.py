from . import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text
from sqlalchemy.sql import func


class Rating(Base):
    __tablename__ = "ratings"

    rating_id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, nullable=True)
    order_id = Column(Integer, nullable=True)
    restaurant_emoji_score = Column(Integer, nullable=True)
    order_emoji_score = Column(Integer, nullable=True)
    restaurant_comment = Column(Text, nullable=True)
    order_comment = Column(Text, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=True)
