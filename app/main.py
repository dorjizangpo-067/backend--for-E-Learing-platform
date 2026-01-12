from fastapi import FastAPI

from .routers import category, users, course
from .auth import auth
from .database import create_db_and_tables

app = FastAPI(
    title="E-Learning Platform API",
    description="API for managing courses, users, and content in an e-learning platform.",
    version="1.0.0",
    contact={
        "name": "E-Learning Support",
        "email": "dorjizangpo75@gmail.com"
    }
)

@app.on_event("startup") 
def on_startup(): 
    create_db_and_tables()

app.include_router(users.router)
app.include_router(course.router)
app.include_router(category.router)
app.include_router(auth.router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}