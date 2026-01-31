import pytest

from app.auth.utilits import create_access_token
from app.env_loader import settings
from app.models.users import User


@pytest.fixture
def admin_headers(session):
    user = User(
        name="Admin", email="admin@example.com", role="admin", hashed_password="hashed"
    )
    # Note: admin email check in auth router might require specific admin email from settings.
    # But category creation checks IsAdmin dependency.
    # Let's create an admin user.
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id, "name": user.name},
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
    )
    return {"Cookie": f"access_token={token}"}


@pytest.mark.asyncio
async def test_create_category(client, session, admin_headers):
    category_data = {"name": "New Category"}
    response = await client.post(
        "/categories/create", json=category_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Category"
