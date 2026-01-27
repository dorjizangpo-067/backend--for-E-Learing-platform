from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .routers import category, users, course
from .auth import auth
from .database import create_db_and_tables, engine
from .limiter import limiter, custom_rate_limit_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield  # App runs here
    engine.dispose()

app = FastAPI(
    lifespan=lifespan,
    title="E-Learning Platform API",
    description="API for managing courses, users, and content in an e-learning platform.",
    version="1.0.0",
    contact={
        "name": "E-Learning Support",
        "email": "dorjizangpo75@gmail.com"
    }
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler) # type: ignore
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(course.router)
app.include_router(category.router)
app.include_router(auth.router)