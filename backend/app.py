# إعدادات الترميز للنصوص العربية
import os
import sys
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import traceback
import json

from core.config import settings
from core.db import engine
from api.routes import orders, debug, selfcheck
from api.routes import analytics
import os
import socketio
from realtime.sio import sio
from api.routes import assign, ws
from api.routes import admin as admin_router

# استيراد النماذج لضمان عمل النظام
from models import Base, Customer, Restaurant, Order, Captain

class UTF8JSONResponse(JSONResponse):
    """JSON Response مع ترميز UTF-8 للنصوص العربية"""
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,  # السماح بالأحرف غير ASCII (العربية)
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

class EncodingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # إصلاح ترميز جميع الاستجابات
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            response.headers["content-type"] = "application/json; charset=utf-8"
        elif "text/" in content_type and "charset" not in content_type:
            response.headers["content-type"] = f"{content_type}; charset=utf-8"
        
        # إضافة headers إضافية للترميز
        response.headers["charset"] = "utf-8"
        
        return response

app = FastAPI(
    title="Movo System API",
    description="نظام إدارة الطلبات والتوصيل",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # إعدادات الترميز للنصوص العربية
    default_response_class=UTF8JSONResponse,
)

# إضافة middleware للترميز
app.add_middleware(EncodingMiddleware)

# CORS (dev-friendly). إذا كان DEBUG مفعّلاً نسمح بأي أصل محلي، بدون Credentials
if settings.DEBUG:
	origin_regex = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
	app.add_middleware(
		CORSMiddleware,
		allow_origin_regex=origin_regex,
		allow_credentials=False,
		allow_methods=["*"],
		allow_headers=["*"],
	)
else:
	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.ALLOWED_ORIGINS,
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

app.add_middleware(
	TrustedHostMiddleware,
	allowed_hosts=["localhost", "127.0.0.1"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
	logger.error(f"Global exception: {exc}")
	logger.error(f"Traceback: {traceback.format_exc()}")
	return JSONResponse(
		status_code=500,
		content={"detail": f"Internal server error: {str(exc)}"}
	)


@app.get("/health")
async def health():
	return {"ok": True}

@app.get("/test-arabic")
async def test_arabic():
	"""اختبار النصوص العربية"""
	return {
		"message": "مرحباً بك في نظام Movo",
		"captain_name": "أحمد محمد",
		"restaurant_name": "مطعم الشام",
		"status": "نجح الاختبار"
	}


app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(debug.router, prefix="/_debug", tags=["debug"])
app.include_router(selfcheck.router, prefix="", tags=["selfcheck"])
app.include_router(assign.router)
app.include_router(ws.router)
app.include_router(analytics.router)
app.include_router(admin_router.router)

# Socket.IO ASGI wrapper
SOCKET_IO_PATH = os.getenv("SOCKET_IO_PATH", "/socket.io")
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path=SOCKET_IO_PATH)


@app.on_event("startup")
async def _startup():
	# log DB URL sans password
	try:
		url = engine.url
		url_str = str(url)
		if getattr(url, "password", None):
			url_str = url_str.replace(url.password, "***")
		logger.info(f"[DB] {url_str}")
	except Exception:
		logger.info("[DB] URL unavailable")


