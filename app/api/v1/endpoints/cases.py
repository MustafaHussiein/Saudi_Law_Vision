"""Cases API endpoints"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.case import Case, CaseStatus, CaseType

router = APIRouter()


class CaseIn(BaseModel):
    case_number: Optional[str] = None
    title: str
    title_ar: Optional[str] = None
    description: Optional[str] = None
    case_type: Optional[str] = "civil"
    status: Optional[str] = "pending"
    client_id: Optional[int] = None
    lawyer_id: Optional[int] = None
    court_name: Optional[str] = None
    judge_name: Optional[str] = None
    filing_date: Optional[str] = None
    next_hearing_date: Optional[str] = None
    estimated_value: Optional[float] = None
    priority: Optional[str] = "normal"
    notes: Optional[str] = None
    is_confidential: bool = False


def _parse_date(val):
    if not val:
        return None
    try:
        return datetime.fromisoformat(str(val))
    except Exception:
        try:
            return datetime.strptime(str(val), "%Y-%m-%d")
        except Exception:
            return None


def _d(c: Case) -> dict:
    return {k: (v.value if hasattr(v, "value") else (str(v) if hasattr(v, "isoformat") else v))
            for k, v in c.__dict__.items() if not k.startswith("_")}


def _next_case_number(db: Session) -> str:
    last = db.query(Case).order_by(Case.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"CASE-{num:06d}"


@router.get("")
def list_cases(
    skip: int = 0,
    limit: int = 50,
    client_id: Optional[int] = None,
    lawyer_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    q = db.query(Case)
    if client_id:
        q = q.filter(Case.client_id == client_id)
    if lawyer_id:
        q = q.filter(Case.lawyer_id == lawyer_id)
    if status_filter:
        try:
            q = q.filter(Case.status == CaseStatus(status_filter))
        except ValueError:
            pass
    cases = q.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": db.query(Case).count(), "cases": [_d(c) for c in cases]}


@router.post("", status_code=201)
def create_case(
    case_in: CaseIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        case_type = CaseType(case_in.case_type or "civil")
    except ValueError:
        case_type = CaseType.CIVIL
    try:
        case_status = CaseStatus(case_in.status or "pending")
    except ValueError:
        case_status = CaseStatus.PENDING

    try:
        case = Case(
            case_number=case_in.case_number or _next_case_number(db),
            title=case_in.title,
            title_ar=case_in.title_ar,
            description=case_in.description,
            case_type=case_type,
            status=case_status,
            client_id=case_in.client_id,
            lawyer_id=case_in.lawyer_id,
            court_name=case_in.court_name,
            judge_name=case_in.judge_name,
            filing_date=_parse_date(case_in.filing_date),
            next_hearing_date=_parse_date(case_in.next_hearing_date),
            estimated_value=case_in.estimated_value,
            priority=case_in.priority or "normal",
            notes=case_in.notes,
            is_confidential=case_in.is_confidential,
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return _d(case)
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))


@router.get("/{case_id}")
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "القضية غير موجودة")
    result = _d(case)
    # Include hearings
    try:
        from app.models.case import Hearing
        result["hearings"] = [
            {"id": h.id, "title": h.title, "hearing_date": str(h.hearing_date),
             "status": h.status.value if hasattr(h.status, "value") else str(h.status),
             "location": h.location}
            for h in db.query(Hearing).filter(Hearing.case_id == case_id).order_by(Hearing.hearing_date).all()
        ]
    except Exception:
        result["hearings"] = []
    return result


@router.put("/{case_id}")
def update_case(
    case_id: int,
    case_in: CaseIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "القضية غير موجودة")
    try:
        for k, v in case_in.model_dump(exclude_unset=True).items():
            if k == "case_type":
                try: setattr(case, k, CaseType(v))
                except: pass
            elif k == "status":
                try: setattr(case, k, CaseStatus(v))
                except: pass
            elif k in ("filing_date", "next_hearing_date"):
                setattr(case, k, _parse_date(v))
            else:
                setattr(case, k, v)
        db.commit()
        db.refresh(case)
        return _d(case)
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))


@router.post("/{case_id}/close")
def close_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "القضية غير موجودة")
    case.status = CaseStatus.CLOSED
    db.commit()
    return {"message": "تم إغلاق القضية", "id": case_id}


@router.delete("/{case_id}")
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "القضية غير موجودة")
    db.delete(case)
    db.commit()
    return {"message": "تم حذف القضية", "id": case_id}
