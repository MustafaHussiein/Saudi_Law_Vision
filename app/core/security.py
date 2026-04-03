"""
Security utilities
File: app/core/security.py

Provides:
  - get_password_hash()
  - verify_password()
  - create_access_token()
  - get_current_active_user()  ← alias from deps.py for backward compatibility
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from passlib.context import CryptContext
from jose import jwt

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ── Backward-compatibility alias ──────────────────────────────────────────────
# Old endpoints did: from app.core.security import get_current_active_user
# This re-exports it so those imports still work
from app.core.deps import get_current_active_user, get_current_user, get_current_superuser
