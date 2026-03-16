import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utilits import create_access_token
from app.env_loader import settings
from app.models.categories import Category
from app.models.courses import Course
from app.models.users import User


@pytest.fixture
async def auth_headers(session: AsyncSession) -> dict[str, str]:
    user = User(
        name="Teacher",
        bio="",
        email="teacher@example.com",
        role="teacher",
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
async def test_create_course(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    # Create category first
    category = Category(name="Programming")
    session.add(category)
    await session.commit()

    course_data = {
        "title": "FastAPI Course",
        "description": "Learn FastAPI",
        "course_url": "vid123",
        "category": "Programming",
    }

    response = await client.post("/courses/", json=course_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "FastAPI Course"


@pytest.mark.asyncio
async def test_get_courses(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    # Create course manually
    user = User(
        name="Author",
        bio="",
        email="author@example.com",
        role="teacher",
        hashed_password="ht",
    )
    category = Category(name="Tech")
    session.add(user)
    session.add(category)
    await session.commit()
    await session.refresh(user)
    await session.refresh(category)

    course = Course(
        title="Intro",
        description="Desc",
        course_url="v1",
        category_id=category.id,
        author_id=user.id,
    )
    session.add(course)
    await session.commit()

    response = await client.get("/courses/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Intro"


@pytest.mark.asyncio
async def test_delete_course(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    # Create category and course owned by the auth_headers user
    category = Category(name="Programming")
    session.add(category)
    await session.commit()

    # We need to get the user ID from the auth_headers to assign correct author_id
    # Or simplified: verify auth_headers creates a user with known attributes.
    # In auth_headers fixture, user email is teacher@example.com.
    # We need that user object or ID.

    statement = select(User).where(User.email == "teacher@example.com")
    result = await session.execute(statement)
    user = result.scalars().first()

    course = Course(
        title="To Delete",
        description="Desc",
        course_url="del",
        category_id=category.id,
        author_id=user.id,  # type: ignore
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)

    response = await client.delete(f"/courses/{course.id}", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_course_invalid_category(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    course_data = {
        "title": "Bad Course",
        "description": "Desc",
        "course_url": "vid",
        "category": "NonExistent",
    }
    # Need to create a category first? No, we want invalid.
    # But code fetches all categories to show in error.
    # Let's create one valid category so the list isn't empty (optional but good).
    category = Category(name="Valid")
    session.add(category)
    await session.commit()

    response = await client.post("/courses/", json=course_data, headers=auth_headers)
    assert response.status_code == 404
    assert "Invalid category" in response.json()["detail"]["error"]


@pytest.mark.asyncio
async def test_delete_course_not_found(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    response = await client.delete("/courses/9999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_course_forbidden(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    # Create course by another user
    other_user = User(
        name="Other", bio="", email="other@ex.com", role="teacher", hashed_password="pw"
    )
    category = Category(name="Math")
    session.add(other_user)
    session.add(category)
    await session.commit()
    await session.refresh(other_user)  # Ensure ID

    course = Course(
        title="Other's Course",
        description="Desc",
        course_url="v",
        category_id=category.id,
        author_id=other_user.id,
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)  # Ensure ID

    response = await client.delete(f"/courses/{course.id}", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_course(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    # Create category and course owned by the auth_headers user
    category = Category(name="Programming")
    session.add(category)
    await session.commit()

    statement = select(User).where(User.email == "teacher@example.com")
    result = await session.execute(statement)
    user = result.scalars().first()

    course = Course(
        title="Original",
        description="Desc",
        course_url="vid",
        category_id=category.id,
        author_id=user.id,  # type: ignore
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)

    update_data = {"title": "Updated"}
    response = await client.patch(
        f"/courses/{course.id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_course_not_found(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    response = await client.patch(
        "/courses/9999", json={"title": "New"}, headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_course_forbidden(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    other_user = User(
        name="Other",
        bio="",
        email="other2@ex.com",
        role="teacher",
        hashed_password="pw",
    )
    category = Category(name="Sci")
    session.add(other_user)
    session.add(category)
    await session.commit()
    await session.refresh(other_user)

    course = Course(
        title="Other's Course",
        description="Desc",
        course_url="v",
        category_id=category.id,
        author_id=other_user.id,
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)

    response = await client.patch(
        f"/courses/{course.id}", json={"title": "Hacked"}, headers=auth_headers
    )
    assert response.status_code == 403
