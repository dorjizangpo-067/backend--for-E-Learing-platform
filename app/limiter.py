from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from fastapi import Request
from fastapi.responses import JSONResponse

# custom handler
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "message": "You have exceeded your request limit. Please try again in a few minutes.",
            "retry_after": exc.detail  # tell user how much time is left
        }
    )

def get_smart_key(request: Request):
    user:dict | None = getattr(request.state, "user", None)
    if user:
        return f"user_{user.get(id)}"

    return get_remote_address(request)

limiter = Limiter(key_func=get_smart_key)