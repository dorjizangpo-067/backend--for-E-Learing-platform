import pytest

from app.schemas.user import UserCreateSchema


@pytest.mark.asyncio
async def test_register_user(client, session):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "student",
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_register_existing_user(client, session):
    user_data = {
        "name": "Test User",
        "email": "existing@example.com",
        "password": "password123",
        "role": "student",
    }
    await client.post("/auth/register", json=user_data)

    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "User with this email already exists."


@pytest.mark.asyncio
async def test_login_user(client, session):
    # Register first
    user_data = {
        "name": "Login User",
        "email": "login@example.com",
        "password": "password123",
        "role": "student",
    }
    await client.post("/auth/register", json=user_data)

    login_data = {"email": "login@example.com", "password": "password123"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.cookies  # Since we set cookie


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, session):
    login_data = {"email": "wrong@example.com", "password": "wrongpassword"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 401
