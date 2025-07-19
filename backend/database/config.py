"""
Database configuration and Base class
إعداد قاعدة البيانات والفئة الأساسية
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from backend.config import settings
import logging
from typing import AsyncGenerator

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Create async database engine with optimized settings
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=settings.database_pool_recycle,
    future=True,  # Enable SQLAlchemy 2.0 features
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Create base class for models
Base = declarative_base() 