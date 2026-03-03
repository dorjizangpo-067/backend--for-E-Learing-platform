# E-Learning Platform Backend

A high-performance backend service built with **FastAPI** + **async**, designed to power a modern online learning platform in Bhutan. It provides secure APIs for user management, course content content delivery, and authentication.

## 🚀 Features

- **Authentication**: Secure JWT-based auth.
- **User Management**: Role-based access (Student, Teacher, Admin).
- **Course Management**: CRUD courses and filter by categories.

## 🛠️ Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern web framework.
- **[Sqlalchemy](https://www.sqlalchemy.org/)**: Database ORM.
- **[uv](https://docs.astral.sh/uv/)**: Python project and package manager.
- **[Alembic](https://alembic.sqlalchemy.org/)**: Database migrations.
- **[SlowAPI](https://pypi.org/project/slowapi/)**: Rate limiting.
- **[Pydantic](https://docs.pydantic.dev/latest/)**: Data Validation
- **[Docker](https://www.docker.com/)**: Containerise Project (comming soon)
- **[Git](https://git-scm.com/)**: Code version Control
- **[VS Code](https://code.visualstudio.com/)**: Conde Editor

## ⚡ Installation

This project uses `uv` for dependency management.

1. **Clone the repository**:

    ```bash
    git clone https://github.com/dorjizangpo-067/e-backend.git
    cd e-backend
    ```

2. **Install dependencies**:

    ```bash
    uv sync
    ```

    This will automatically create a virtual environment (`.venv`) and install all required packages.
   
## 🔐 Environment Variables

Create a `.env` file in the root directory:

```ini
sqlite_url=sqlite:///database.db
secret_key=your-super-secret-key-change-this
algorithm=HS256
access_token_expire_minutes=30
admin_email=admin@example.com
```

## 🏃‍♂️ Running the App

### Development Server

Run the migration(alembic) to database:

```bash
alembic upgrade head
```

Run the application with auto-reload enabled:

```bash
uv run fastapi dev app/main.py
```

The API will be available at: `http://127.0.0.1:8000`  
Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

## 🧪 Running Tests

Run the test suite with `pytest`:

```bash
uv run pytest
```



## 📂 Project Structure

```text
e-backend/
├── migrations          # Database Migrations
|   ├── versions/
|   ├── env.py
|   ├── ...
├── app/
│   ├── auth/           # Authentication logic & utilities
│   ├── models/         # Sqlalchemy database tables
│   ├── routers/        # API endpoints (users, courses, categories)
│   ├── schemas/        # Pydantic data validation schemas
│   ├── database.py     # DB session and connection
│   ├── dependencies.py # Dependency injection (e.g. current user)
│   ├── main.py         # App entry point
│   ├── limiter.py      # Rate limiting config
│   └── env_loader.py   # Settings loading
├── tests/              # Pytest modules
├── .env                # Environment variables (git-ignored)
├── pyproject.toml      # Project configuration & dependencies
└── uv.lock             # Locked dependency versions
```

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes.
4. Push to the branch.
5. Open a Pull Request.


