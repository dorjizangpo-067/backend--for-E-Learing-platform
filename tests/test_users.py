import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utilits import create_access_token
from app.env_loader import settings
from app.models.users import User


@pytest.fixture
async def admin_headers(session: AsyncSession) -> dict[str, str]:
    user = User(
        name="Admin",
        bio="",
        email="admin@example.com",
        role="admin",
        hashed_password="hashed",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id, "name": user.name},
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
    )
    return {"Cookie": f"access_token={token}"}


@pytest.mark.asyncio
async def test_get_users(client: AsyncClient, session: AsyncSession, admin_headers: dict[str, str]) -> None:
    # Create a user first
    user = User(
        name="Test User",
        bio="",
        email="test@example.com",
        role="student",
        hashed_password="hashed",
    )
    session.add(user)
    await session.commit()

    response = await client.get("/users/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
