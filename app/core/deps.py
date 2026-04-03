"""
FastAPI Dependencies
File: app/core/deps.py

THIS FILE WAS MISSING — that's why ALL API routes failed to load.

Contains:
  - get_db()                  → SQLAlchemy session per request
  - get_current_user()        → Decode JWT token → User object
  - get_current_active_user() → Same + checks is_active
  - get_current_superuser()   → Same + checks is_superuser
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User

# Points to POST /api/v1/auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator:
    """
    Yield a database session, close it after the request.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Decode JWT token and return the User.
    Raises 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # sub is stored as str(user.id) — convert back to int
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
    except (ValueError, TypeError):
        # Fallback: maybe old tokens stored email instead of id
        user = db.query(User).filter(User.email == user_id).first()

    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Same as get_current_user but also checks is_active.
    Usage: current_user: User = Depends(get_current_active_user)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Same as get_current_active_user but also checks is_superuser.
    Usage: current_user: User = Depends(get_current_superuser)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
