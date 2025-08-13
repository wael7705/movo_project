import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from backend.app import app
from backend.database.config import Base
from backend.api.routes import public_orders as public_orders_module
from backend.models.orders import Order


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def test_db_session(monkeypatch) -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        future=True,
        echo=False,
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_maker() as session:
            yield session

    monkeypatch.setattr(public_orders_module, "get_db", override_get_db)

    try:
        yield test_session_maker()
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_get_public_orders_empty(test_db_session):
    transport = ASGITransport(app=app, lifespan="off")
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/orders")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.asyncio
async def test_get_public_orders_with_data(test_db_session):
    async with test_db_session as session:
        order = Order(
            customer_id=1,
            restaurant_id=1,
            total_price_customer=10,
            total_price_restaurant=8,
            delivery_fee=2,
        )
        session.add(order)
        await session.commit()

    transport = ASGITransport(app=app, lifespan="off")
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/orders")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["order_id"] == 1

