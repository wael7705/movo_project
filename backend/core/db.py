from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from .config import settings

# استيراد النماذج لضمان عمل النظام
from models import Base, Customer, Restaurant, Order, Captain

engine = create_async_engine(
	settings.DATABASE_URL,
	pool_pre_ping=True,
	future=True,
)

AsyncSessionLocal = async_sessionmaker(
	bind=engine,
	class_=AsyncSession,
	expire_on_commit=False,
	autoflush=False,
	autocommit=False,
)


async def get_session() -> AsyncSession:
	"""Get database session."""
	session = AsyncSessionLocal()
	return session


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
