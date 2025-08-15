"""
Modern FastAPI application for MOVO delivery platform with AI support
تطبيق FastAPI الحديث لمنصة MOVO للتوصيل مع دعم الذكاء الاصطناعي
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any
from sqlalchemy import text

from .config import settings  # جعل الاستيراد نسبيًا لضمان العمل من جذر المشروع
from .database.database import init_db, close_db, health_check, get_db
from .api.routes import orders, captains, restaurants, customers, chat
from .api.routes import public_orders

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting MOVO Delivery Platform...")
    # Initialize database on startup to ensure proper connectivity
    try:
        await init_db()
        logger.info("✅ Database initialized and ready")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Continue startup; endpoints that hit DB will surface detailed errors
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down MOVO Delivery Platform...")
    try:
        await close_db()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database connections: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Modern delivery platform with AI support",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
# CORS: allow local Vite dev servers. Added 127.0.0.1 alongside localhost for consistency.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with logging"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc) if settings.debug else "Something went wrong"}
    )


# Health check endpoint
# Keep the payload minimal and stable for uptime probes.
@app.get("/health", tags=["Health"])
async def health_endpoint() -> Dict[str, Any]:
    return {"ok": True}


# Simple request logging middleware to trace requests lifecycle.
@app.middleware("http")
async def log_requests(request, call_next):
    print("→", request.method, request.url.path)
    response = await call_next(request)
    print("←", response.status_code, request.url.path)
    return response


# Database ping endpoint
@app.get("/db_ping")
async def db_ping(db=Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"ok": True, "result": result.scalar_one()}
    except Exception as e:
        logger.error(f"DB ping failed: {e}")
        raise HTTPException(status_code=500, detail="Database unreachable")


# Versioned Database ping for clients that prepend the API prefix
@app.get("/api/v1/db_ping")
async def db_ping_v1(db=Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"ok": True, "result": result.scalar_one()}
    except Exception as e:
        logger.error(f"DB ping failed: {e}")
        raise HTTPException(status_code=500, detail="Database unreachable")


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with platform information"""
    return {
        "message": "Welcome to MOVO Delivery Platform",
        "version": settings.version,
        "status": "running",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health"
    }


# Include API routes
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(public_orders.router)
app.include_router(captains.router, prefix="/api/v1/captains", tags=["Captains"])
app.include_router(restaurants.router, prefix="/api/v1/restaurants", tags=["Restaurants"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    ) 