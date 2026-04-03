"""Reminders API - with permissions"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.reminder import Reminder, ReminderStatus, ReminderPriority

router = APIRouter()


class ReminderIn(BaseModel):
    title: str
    title_ar: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = "normal"
    assigned_to_id: Optional[int] = None
    client_id: Optional[int] = None


def _d(r: Reminder) -> dict:
    return {k: (v.value if hasattr(v, "value") else (str(v) if hasattr(v, "isoformat") else v))
            for k, v in r.__dict__.items() if not k.startswith("_")}


def _parse_priority(p: str):
    try: return ReminderPriority(p)
    except: return ReminderPriority.NORMAL


@router.get("")
def list_reminders(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Admin sees all, regular user sees only their own"""
    q = db.query(Reminder)
    
    # FIX: Permissions
    if not current_user.is_superuser:
        q = q.filter(
            (Reminder.created_by_id == current_user.id) | 
            (Reminder.assigned_to_id == current_user.id)
        )
    
    if status_filter:
        try: q = q.filter(Reminder.status == ReminderStatus(status_filter))
        except ValueError: pass
    
    reminders = q.order_by(Reminder.due_date.asc()).offset(skip).limit(limit).all()
    return {"total": q.count(), "reminders": [_d(r) for r in reminders]}


@router.post("", status_code=201)
def create_reminder(reminder_in: ReminderIn, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)) -> Any:
    due = None
    if reminder_in.due_date:
        try: due = datetime.fromisoformat(reminder_in.due_date.replace("Z", "+00:00"))
        except:
            try: due = datetime.strptime(reminder_in.due_date, "%Y-%m-%d")
            except: pass
    try:
        r = Reminder(
            title=reminder_in.title, title_ar=reminder_in.title_ar,
            description=reminder_in.description, due_date=due,
            priority=_parse_priority(reminder_in.priority or "normal"),
            status=ReminderStatus.PENDING,
            created_by_id=current_user.id,
            assigned_to_id=reminder_in.assigned_to_id,
            client_id=reminder_in.client_id
        )
        db.add(r); db.commit(); db.refresh(r)
        return _d(r)
    except Exception as e:
        db.rollback(); raise HTTPException(500, str(e))


@router.get("/{reminder_id}")
def get_reminder(reminder_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_active_user)) -> Any:
    r = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not r: raise HTTPException(404, "التذكير غير موجود")
    
    # FIX: Permission check
    if not current_user.is_superuser:
        if r.created_by_id != current_user.id and r.assigned_to_id != current_user.id:
            raise HTTPException(403, "غير مصرح")
    
    return _d(r)


@router.put("/{reminder_id}")
def update_reminder(reminder_id: int, reminder_in: ReminderIn, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)) -> Any:
    r = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not r: raise HTTPException(404, "التذكير غير موجود")
    
    # FIX: Permission check
    if not current_user.is_superuser:
        if r.created_by_id != current_user.id and r.assigned_to_id != current_user.id:
            raise HTTPException(403, "غير مصرح")
    
    for k, v in reminder_in.model_dump(exclude_unset=True).items():
        if k == "priority": setattr(r, k, _parse_priority(v))
        elif k == "due_date" and v:
            try: setattr(r, k, datetime.fromisoformat(v))
            except: pass
        else: setattr(r, k, v)
    db.commit(); db.refresh(r)
    return _d(r)


@router.post("/{reminder_id}/complete")
def complete_reminder(reminder_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)) -> Any:
    r = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not r: raise HTTPException(404, "التذكير غير موجود")
    
    # FIX: Permission check
    if not current_user.is_superuser:
        if r.created_by_id != current_user.id and r.assigned_to_id != current_user.id:
            raise HTTPException(403, "غير مصرح")
    
    r.status = ReminderStatus.COMPLETED
    db.commit()
    return {"message": "تم الإكمال", "id": reminder_id}


@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)) -> Any:
    r = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not r: raise HTTPException(404, "التذكير غير موجود")
    
    # Only creator or admin can delete
    if not current_user.is_superuser and r.created_by_id != current_user.id:
        raise HTTPException(403, "فقط منشئ التذكير يمكنه حذفه")
    
    db.delete(r); db.commit()
    return {"message": "تم الحذف", "id": reminder_id}
