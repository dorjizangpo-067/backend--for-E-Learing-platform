import pytest

from app.auth.utilits import create_access_token
from app.env_loader import settings
from app.models.users import User


@pytest.fixture
def student_headers(session):
    user = User(
        name="Student",
        email="student@example.com",
        role="student",
        hashed_password="pw",
    )
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
async def test_admin_required_endpoint_forbidden(client, session, student_headers):
    # /categories/create requires admin
    response = await client.post(
        "/categories/create", json={"name": "Forbidden"}, headers=student_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_teacher_required_endpoint_forbidden(client, session, student_headers):
    # Create category otherwise we get 404 from body before permission check failure?
    # (Checking if permission check is indeed bypassed or if verify order is weird)
    from app.models.categories import Category

    category = Category(name="Math")
    session.add(category)
    session.commit()

    # /courses/ create requires teacher or admin
    course_data = {
        "title": "Bad Course",
        "description": "Desc",
        "video_id": "vid",
        "category": "Math",
    }
    response = await client.post("/courses/", json=course_data, headers=student_headers)
    assert response.status_code == 403
