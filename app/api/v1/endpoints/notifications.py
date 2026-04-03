"""Notifications API - user's own only"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()


def _d(n: Notification) -> dict:
    return {k: (v.value if hasattr(v, "value") else (str(v) if hasattr(v, "isoformat") else v))
            for k, v in n.__dict__.items() if not k.startswith("_")}


@router.get("")
def list_notifications(skip: int = 0, limit: int = 50, unread_only: bool = False,
                      db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    q = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    notifs = q.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read == False
    ).count()
    return {"total": q.count(), "unread_count": unread_count, "notifications": [_d(n) for n in notifs]}


@router.get("/{notification_id}")
def get_notification(notification_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_active_user)) -> Any:
    n = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == current_user.id
    ).first()
    if not n: raise HTTPException(404, "الإشعار غير موجود")
    return _d(n)


@router.post("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_active_user)) -> Any:
    n = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == current_user.id
    ).first()
    if not n: raise HTTPException(404, "الإشعار غير موجود")
    n.is_read = True; n.read_at = datetime.utcnow()
    db.commit()
    return {"message": "تم التحديد كمقروء", "id": notification_id}


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    return {"message": f"تم تحديد {count} إشعار كمقروء", "updated": count}


@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_active_user)) -> Any:
    n = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == current_user.id
    ).first()
    if not n: raise HTTPException(404, "الإشعار غير موجود")
    db.delete(n); db.commit()
    return {"message": "تم الحذف", "id": notification_id}
