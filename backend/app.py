from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from loguru import logger

from .core.config import settings
from .core.db import engine
from backend.api.routes import orders, debug


app = FastAPI()

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


@app.get("/health")
async def health():
	return {"ok": True}


app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(debug.router, prefix="/_debug", tags=["debug"]) 


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


