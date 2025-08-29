from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from .config import settings
from sqlalchemy import text as sa_text

# استيراد النماذج لضمان عمل النظام
from models import Base, Customer, Restaurant, Order, Captain

engine = create_async_engine(
	settings.DATABASE_URL,
	pool_pre_ping=True,
	pool_recycle=1800,
	pool_size=15,
	max_overflow=25,
	future=True,
)

AsyncSessionLocal = async_sessionmaker(
	bind=engine,
	class_=AsyncSession,
	expire_on_commit=False,
	autoflush=False,
	autocommit=False,
)


async def get_session():
	"""Get database session (FastAPI Depends) with safe close and timeout."""
	async with AsyncSessionLocal() as session:
		try:
			await session.execute(sa_text("SET SESSION statement_timeout = 8000"))
		except Exception:
			pass
		yield session


@asynccontextmanager
async def get_session_context():
	session: AsyncSession = AsyncSessionLocal()
	try:
		yield session
	except Exception:
		await session.rollback()
		raise
	finally:
		await session.close()
