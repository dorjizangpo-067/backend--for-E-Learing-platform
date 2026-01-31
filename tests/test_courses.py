import pytest

from app.auth.utilits import create_access_token
from app.env_loader import settings
from app.models.categories import Category
from app.models.courses import Course
from app.models.users import User


@pytest.fixture
def auth_headers(session):
    user = User(
        name="Teacher",
        email="teacher@example.com",
        role="teacher",
        hashed_password="hashed",
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
async def test_create_course(client, session, auth_headers):
    # Create category first
    category = Category(name="Programming")
    session.add(category)
    session.commit()

    course_data = {
        "title": "FastAPI Course",
        "description": "Learn FastAPI",
        "video_id": "vid123",
        "category": "Programming",
    }

    response = await client.post("/courses/", json=course_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    # The response wrapper is {"courses": ...} based on reading routers/course.py
    assert data["courses"]["title"] == "FastAPI Course"


@pytest.mark.asyncio
async def test_get_courses(client, session):
    # Create course manually
    user = User(
        name="Author", email="author@example.com", role="teacher", hashed_password="ht"
    )
    category = Category(name="Tech")
    session.add(user)
    session.add(category)
    session.commit()
    session.refresh(user)
    session.refresh(category)

    course = Course(
        title="Intro",
        description="Desc",
        video_id="v1",
        category_id=category.id,
        author_id=user.id,
    )
    session.add(course)
    session.commit()

    response = await client.get("/courses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["courses"]) == 1
    assert data["courses"][0]["title"] == "Intro"


@pytest.mark.asyncio
async def test_delete_course(client, session, auth_headers):
    # Create category and course owned by the auth_headers user
    category = Category(name="Programming")
    session.add(category)
    session.commit()

    # We need to get the user ID from the auth_headers to assign correct author_id
    # Or simplified: verify auth_headers creates a user with known attributes.
    # In auth_headers fixture, user email is teacher@example.com.
    # We need that user object or ID.

    statement = (
        pytest.importorskip("sqlmodel")
        .select(User)
        .where(User.email == "teacher@example.com")
    )
    # Using session from outer scope? No, use local session
    user = session.exec(statement).first()

    course = Course(
        title="To Delete",
        description="Desc",
        video_id="del",
        category_id=category.id,
        author_id=user.id,
    )
    session.add(course)
    session.commit()
    session.refresh(course)

    response = await client.delete(f"/courses/{course.id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify deletion
    deleted = session.get(Course, course.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_create_course_invalid_category(client, session, auth_headers):
    course_data = {
        "title": "Bad Course",
        "description": "Desc",
        "video_id": "vid",
        "category": "NonExistent",
    }
    # Need to create a category first? No, we want invalid.
    # But code fetches all categories to show in error.
    # Let's create one valid category so the list isn't empty (optional but good).
    category = Category(name="Valid")
    session.add(category)
    session.commit()

    response = await client.post("/courses/", json=course_data, headers=auth_headers)
    assert response.status_code == 404
    assert "Invalid category" in response.json()["detail"]["error"]


@pytest.mark.asyncio
async def test_delete_course_not_found(client, session, auth_headers):
    response = await client.delete("/courses/9999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_course_forbidden(client, session, auth_headers):
    # Create course by another user
    other_user = User(
        name="Other", email="other@ex.com", role="teacher", hashed_password="pw"
    )
    category = Category(name="Math")
    session.add(other_user)
    session.add(category)
    session.commit()
    session.refresh(other_user)  # Ensure ID

    course = Course(
        title="Other's Course",
        description="Desc",
        video_id="v",
        category_id=category.id,
        author_id=other_user.id,
    )
    session.add(course)
    session.commit()
    session.refresh(course)  # Ensure ID

    response = await client.delete(f"/courses/{course.id}", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_course(client, session, auth_headers):
    # Create category and course owned by the auth_headers user
    category = Category(name="Programming")
    session.add(category)
    session.commit()

    statement = (
        pytest.importorskip("sqlmodel")
        .select(User)
        .where(User.email == "teacher@example.com")
    )
    user = session.exec(statement).first()

    course = Course(
        title="Original",
        description="Desc",
        video_id="vid",
        category_id=category.id,
        author_id=user.id,
    )
    session.add(course)
    session.commit()
    session.refresh(course)

    update_data = {"title": "Updated"}
    response = await client.patch(
        f"/courses/{course.id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["course"]["title"] == "Updated"


@pytest.mark.asyncio
async def test_update_course_not_found(client, session, auth_headers):
    response = await client.patch(
        "/courses/9999", json={"title": "New"}, headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_course_forbidden(client, session, auth_headers):
    other_user = User(
        name="Other", email="other2@ex.com", role="teacher", hashed_password="pw"
    )
    category = Category(name="Sci")
    session.add(other_user)
    session.add(category)
    session.commit()
    session.refresh(other_user)

    course = Course(
        title="Other's Course",
        description="Desc",
        video_id="v",
        category_id=category.id,
        author_id=other_user.id,
    )
    session.add(course)
    session.commit()
    session.refresh(course)

    response = await client.patch(
        f"/courses/{course.id}", json={"title": "Hacked"}, headers=auth_headers
    )
    assert response.status_code == 403
