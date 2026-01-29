from pwdlib import PasswordHash

import jwt
from datetime import datetime, timezone, timedelta

hashed_hasdher = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """hash plain password"""
    return hashed_hasdher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verify plain password with hashed password"""
    return hashed_hasdher.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, secret_key: str, algorithm: str, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt
