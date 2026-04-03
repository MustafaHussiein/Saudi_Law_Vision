"""Lawyers API endpoints"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_active_user          # FIX: was from security
from app.models.user import User, UserRole                  # FIX: was from app.models

router = APIRouter()


class LawyerUpdateIn(BaseModel):
    full_name: str = None
    full_name_ar: str = None
    phone: str = None
    license_number: str = None
    specialization: str = None
    bio: str = None


def _d(u: User) -> dict:
    return {"id": u.id, "email": u.email, "full_name": u.full_name,
            "full_name_ar": u.full_name_ar, "phone": u.phone,
            "license_number": u.license_number, "specialization": u.specialization,
            "bio": u.bio, "is_active": u.is_active, "created_at": str(u.created_at)}


@router.get("")                                             # FIX: no trailing slash
def list_lawyers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_active_user)) -> Any:
    lawyers = db.query(User).filter(User.role == UserRole.LAWYER).offset(skip).limit(limit).all()
    return {"total": len(lawyers), "lawyers": [_d(l) for l in lawyers]}


@router.get("/{lawyer_id}")
def get_lawyer(lawyer_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_active_user)) -> Any:
    l = db.query(User).filter(User.id == lawyer_id, User.role == UserRole.LAWYER).first()
    if not l: raise HTTPException(404, "المحامي غير موجود")
    return _d(l)


@router.put("/{lawyer_id}")                                 # FIX: was "/{id}" with trailing slash, raw dict
def update_lawyer(lawyer_id: int, lawyer_in: LawyerUpdateIn, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)) -> Any:
    l = db.query(User).filter(User.id == lawyer_id, User.role == UserRole.LAWYER).first()
    if not l: raise HTTPException(404, "المحامي غير موجود")
    for k, v in lawyer_in.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(l, k, v)
    db.commit(); db.refresh(l)
    return _d(l)


@router.get("/{lawyer_id}/cases")
def get_lawyer_cases(lawyer_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_active_user)) -> Any:
    l = db.query(User).filter(User.id == lawyer_id, User.role == UserRole.LAWYER).first()
    if not l: raise HTTPException(404, "المحامي غير موجود")
    try:
        from app.models.case import Case                   # FIX: Case from case.py not client.py
        cases = db.query(Case).filter(Case.lawyer_id == lawyer_id).all()
        return [{"id": c.id, "case_number": c.case_number, "title": c.title,
                 "status": c.status.value if hasattr(c.status, "value") else str(c.status)}
                for c in cases]
    except Exception:
        return []


@router.get("/{lawyer_id}/statistics")
def lawyer_statistics(lawyer_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)) -> Any:
    l = db.query(User).filter(User.id == lawyer_id, User.role == UserRole.LAWYER).first()
    if not l: raise HTTPException(404, "المحامي غير موجود")
    try:
        from app.models.case import Case, CaseStatus       # FIX: correct module
        total  = db.query(Case).filter(Case.lawyer_id == lawyer_id).count()
        active = db.query(Case).filter(Case.lawyer_id == lawyer_id, Case.status == CaseStatus.ACTIVE).count()
        closed = db.query(Case).filter(Case.lawyer_id == lawyer_id, Case.status == CaseStatus.CLOSED).count()
    except Exception:
        total, active, closed = 0, 0, 0
    return {"lawyer_id": lawyer_id, "lawyer_name": l.full_name,
            "total_cases": total, "active_cases": active, "closed_cases": closed}
