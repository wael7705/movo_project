"""
Weather models
نماذج الطقس
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from ..database.config import Base


class WeatherLog(Base):
    """Weather log model"""
    __tablename__ = "weather_log"
    
    weather_id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    weather_condition = Column(String(50), nullable=False)  # sunny, cloudy, rainy, stormy, etc.
    temperature_celsius = Column(DECIMAL(4, 1), nullable=False)
    humidity_percent = Column(Integer)  # 0-100
    wind_speed_kmh = Column(DECIMAL(5, 2))
    visibility_km = Column(DECIMAL(4, 2))
    precipitation_mm = Column(DECIMAL(5, 2), default=0)
    recorded_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("humidity_percent BETWEEN 0 AND 100"),
        CheckConstraint("temperature_celsius BETWEEN -50 AND 60"),
        CheckConstraint("wind_speed_kmh >= 0"),
        CheckConstraint("visibility_km >= 0"),
        CheckConstraint("precipitation_mm >= 0"),
    ) 