"""Auth endpoints - Creates BOTH User AND Client on registration"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.core.deps import get_current_active_user
from app.models.user import User, UserRole
from app.models.client import Client

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class UserRegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    full_name_ar: str = None
    phone: str = None


@router.post("/login", response_model=Token)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """Login - returns token AND sets cookie"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Set cookie for iframe/img authentication
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=201)
def register(user_in: UserRegisterIn, db: Session = Depends(get_db)) -> Any:
    """
    Register new user - Creates BOTH:
    1. User record (for login)
    2. Client record (for clients list)
    """
    # Check if email already exists
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    try:
        # 1. Create User (for login)
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            full_name_ar=user_in.full_name_ar,
            phone=user_in.phone,
            hashed_password=get_password_hash(user_in.password),
            role=UserRole.CLIENT,
            is_active=True
        )
        db.add(user)
        db.flush()  # Get user.id without committing
        
        # 2. Create Client (for clients list)
        client = Client(
            full_name=user_in.full_name,
            full_name_ar=user_in.full_name_ar,
            email=user_in.email,
            phone=user_in.phone,
            is_active=True,
            notes=f"Registered via portal (User ID: {user.id})"
        )
        db.add(client)
        
        db.commit()
        db.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "message": "User and client created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "full_name_ar": current_user.full_name_ar,
        "phone": current_user.phone,
        "role": current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role),
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    }


@router.post("/logout")
def logout(response: Response) -> Any:
    """Logout - clear cookie"""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}