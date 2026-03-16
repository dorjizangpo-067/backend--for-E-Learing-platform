import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, session: AsyncSession) -> None:
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "student",
        "bio": "",
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_register_existing_user(
    client: AsyncClient, session: AsyncSession
) -> None:
    user_data = {
        "name": "Test User",
        "email": "existing@example.com",
        "password": "password123",
        "role": "student",
        "bio": "",
    }
    await client.post("/auth/register", json=user_data)

    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "User with this email already exists."


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, session: AsyncSession) -> None:
    # Register first
    user_data = {
        "name": "Login User",
        "email": "login@example.com",
        "password": "password123",
        "role": "student",
        "bio": "",
    }
    await client.post("/auth/register", json=user_data)

    login_data = {"email": "login@example.com", "password": "password123"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_invalid_credentials(
    client: AsyncClient, session: AsyncSession
) -> None:
    login_data = {"email": "wrong@example.com", "password": "wrongpassword"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 401
