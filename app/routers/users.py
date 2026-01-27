from fastapi import APIRouter, Depends, HTTPException, Request

from ..limiter import limiter

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/")
@limiter.limit("10/minute")
def get_users(request: Request):
    """  get all users  """
    return {"message": "List of users"}