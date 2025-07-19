"""
Modern database configuration with async support for MOVO delivery platform
إعداد قاعدة البيانات الحديثة مع دعم غير متزامن لمنصة MOVO للتوصيل
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .config import engine, AsyncSessionLocal, Base
import logging
from typing import AsyncGenerator

# Configure logging
logger = logging.getLogger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with dependency injection"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables with async support"""
    try:
        logger.info("🔄 Initializing database...")
        
        async with engine.begin() as conn:
            # Import all models to ensure they are registered with Base
            from backend.models import (
                Customer, CustomerAddress, Restaurant, RestaurantPhone, 
                MenuItem, MenuItemOption, Order, OrderStageDuration, 
                OrderDiscount, Captain, WeatherLog, Rating, Note, 
                Employee, Issue, CallLog, Discount, AIDecisionLog, 
                AIFailure, AlertLog
            )
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("✅ Database initialized successfully")
        
        # Test connection
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("✅ Database connection test successful")
            
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise


async def close_db():
    """Close database connections"""
    try:
        await engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


# Health check function
async def health_check() -> dict:
    """Check database health"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1 as health"))
            result.fetchone()
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)} 