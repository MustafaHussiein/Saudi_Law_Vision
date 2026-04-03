"""Users API endpoints - FIXED with password and permissions"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole

router = APIRouter()


class UserCreateIn(BaseModel):
    email: EmailStr
    password: str                    # FIX: was missing - NOW REQUIRED
    full_name: str
    full_name_ar: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "client"
    is_active: bool = True


class UserUpdateIn(BaseModel):
    full_name: Optional[str] = None
    full_name_ar: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChangeIn(BaseModel):
    current_password: str
    new_password: str


def _d(u: User) -> dict:
    return {"id": u.id, "email": u.email, "full_name": u.full_name,
            "full_name_ar": u.full_name_ar, "phone": u.phone,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
            "is_active": u.is_active, "is_superuser": u.is_superuser,
            "license_number": u.license_number, "specialization": u.specialization,
            "created_at": str(u.created_at), "last_login": str(u.last_login) if u.last_login else None}


@router.get("")
def list_users(skip: int = 0, limit: int = 100, role: Optional[str] = None,
               db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    """List users - only admins can see all users"""
    if not current_user.is_superuser:
        raise HTTPException(403, "فقط المسؤول يمكنه رؤية جميع المستخدمين")
    q = db.query(User)
    if role:
        try: q = q.filter(User.role == UserRole(role))
        except ValueError: pass
    return {"total": q.count(), "users": [_d(u) for u in q.offset(skip).limit(limit).all()]}


@router.post("", status_code=201)
def create_user(user_in: UserCreateIn, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_active_user)) -> Any:
    """Create user - only admins"""
    if not current_user.is_superuser:
        raise HTTPException(403, "فقط المسؤول يمكنه إنشاء مستخدمين")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(409, "البريد الإلكتروني مسجل بالفعل")
    try: role = UserRole(user_in.role)
    except: role = UserRole.CLIENT
    
    # FIX: hash the password before saving
    u = User(
        email=user_in.email,
        full_name=user_in.full_name,
        full_name_ar=user_in.full_name_ar,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),  # FIX: was missing
        role=role,
        is_active=user_in.is_active
    )
    db.add(u); db.commit(); db.refresh(u)
    return _d(u)


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get own profile - any user"""
    return _d(current_user)


@router.put("/profile")
def update_profile(user_in: UserUpdateIn, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_active_user)) -> Any:
    """Update own profile - any user"""
    for k, v in user_in.model_dump(exclude_unset=True, exclude_none=True).items():
        if k == "role" and not current_user.is_superuser:
            continue  # Only admin can change role
        if k == "role":
            try: setattr(current_user, k, UserRole(v))
            except: pass
        else:
            setattr(current_user, k, v)
    db.commit(); db.refresh(current_user)
    return _d(current_user)


@router.post("/profile/change-password")
def change_password(pwd_in: PasswordChangeIn, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)) -> Any:
    """Change own password"""
    if not verify_password(pwd_in.current_password, current_user.hashed_password):
        raise HTTPException(400, "كلمة المرور الحالية غير صحيحة")
    current_user.hashed_password = get_password_hash(pwd_in.new_password)
    db.commit()
    return {"message": "تم تغيير كلمة المرور بنجاح"}


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_active_user)) -> Any:
    """Get user by ID - admin or self"""
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(403, "غير مصرح")
    u = db.query(User).filter(User.id == user_id).first()
    if not u: raise HTTPException(404, "المستخدم غير موجود")
    return _d(u)


@router.put("/{user_id}")
def update_user(user_id: int, user_in: UserUpdateIn, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_active_user)) -> Any:
    """Update user - admin or self (limited)"""
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(403, "غير مصرح")
    u = db.query(User).filter(User.id == user_id).first()
    if not u: raise HTTPException(404, "المستخدم غير موجود")
    
    for k, v in user_in.model_dump(exclude_unset=True, exclude_none=True).items():
        # Only admin can change role and is_active
        if k in ("role", "is_active") and not current_user.is_superuser:
            continue
        if k == "role":
            try: setattr(u, k, UserRole(v))
            except: pass
        else:
            setattr(u, k, v)
    db.commit(); db.refresh(u)
    return _d(u)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_active_user)) -> Any:
    """Delete user - admin only"""
    if not current_user.is_superuser:
        raise HTTPException(403, "فقط المسؤول يمكنه حذف المستخدمين")
    u = db.query(User).filter(User.id == user_id).first()
    if not u: raise HTTPException(404, "المستخدم غير موجود")
    if u.id == current_user.id:
        raise HTTPException(400, "لا يمكنك حذف حسابك الخاص")
    db.delete(u); db.commit()
    return {"message": "تم الحذف", "id": user_id}