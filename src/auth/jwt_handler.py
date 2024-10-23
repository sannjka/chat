from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status, Depends
import jwt

from src.config import get_settings, Settings


settings = get_settings()

def create_access_token(
        user: str, expires_delta: timedelta | None = None,
    ) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        'sub': user,
        'exp': expire,
    }

    token = jwt.encode(payload, settings.SECRET_KEY,
                       algorithm=settings.ALGORITHM)
    return token

def verify_access_token(token: str,) -> dict:
    try:
        data = jwt.decode(token, settings.SECRET_KEY,
                          algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return data
