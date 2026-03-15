import os
import sys
from typing import AsyncGenerator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

test_env = {
    "POSTGRESQL_URL": "sqlite+aiosqlite:///:memory:",
    "SECRET_KEY": "testsecret",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
    "ADMIN_EMAIL": "admin@example.com",
}
for key, value in test_env.items():
    os.environ.setdefault(key, value)

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# module-level in-memory async engine and session factory used by tests
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(name="session")
async def session_fixture() -> AsyncSession:  # type: ignore
    # recreate schema at start of each test to isolate state
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestSession() as session:
        yield session  # type: ignore


@pytest.fixture(name="client")
async def client_fixture(session: AsyncSession) -> AsyncClient:  # type: ignore
    # ensure the app uses our test engine for lifespan and dependencies
    import app.database as _database
    import app.main as _main

    _database.engine = test_engine
    _main.engine = test_engine

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestSession() as s:
            yield s

    app.dependency_overrides[get_db] = override_get_db

    # ensure tables exist on the test engine before startup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client  # type: ignore

    app.dependency_overrides.clear()
