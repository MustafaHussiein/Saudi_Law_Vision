"""Analytics API endpoints"""
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.deps import get_current_active_user          # FIX: was from security
from app.models.user import User                            # FIX: was from app.models
from app.models.reminder import Reminder, ReminderStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.client import Client                        # FIX: was missing

router = APIRouter()


@router.get("/dashboard")
def dashboard_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    r = {s.value: 0 for s in ReminderStatus}
    for status, cnt in db.query(Reminder.status, func.count(Reminder.id)).group_by(Reminder.status).all():
        r[status.value if hasattr(status, "value") else str(status)] = cnt

    t = {s.value: 0 for s in TicketStatus}
    for status, cnt in db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all():
        t[status.value if hasattr(status, "value") else str(status)] = cnt

    # FIX: Case imported safely — only if model exists
    case_total = 0
    case_by_status = {}
    try:
        from app.models.case import Case, CaseStatus       # FIX: Case in case.py not client.py
        for status, cnt in db.query(Case.status, func.count(Case.id)).group_by(Case.status).all():
            case_by_status[status.value if hasattr(status, "value") else str(status)] = cnt
        case_total = db.query(func.count(Case.id)).scalar() or 0
    except Exception:
        pass

    return {
        "reminders": {"total": db.query(func.count(Reminder.id)).scalar() or 0, "by_status": r},
        "tickets":   {"total": db.query(func.count(Ticket.id)).scalar() or 0,   "by_status": t},
        "cases":     {"total": case_total, "by_status": case_by_status},
        "clients":   {"total": db.query(func.count(Client.id)).scalar() or 0},  # FIX: Client now imported
        "quick": {
            "pending":     r.get("pending", 0),
            "in_progress": r.get("in_progress", 0),
            "waiting":     t.get("open", 0),
        }
    }


@router.get("/reminders/stats")
def reminder_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    now = datetime.utcnow()
    return {
        "total":       db.query(func.count(Reminder.id)).scalar() or 0,
        "pending":     db.query(func.count(Reminder.id)).filter(Reminder.status == ReminderStatus.PENDING).scalar() or 0,
        "in_progress": db.query(func.count(Reminder.id)).filter(Reminder.status == ReminderStatus.IN_PROGRESS).scalar() or 0,
        "completed":   db.query(func.count(Reminder.id)).filter(Reminder.status == ReminderStatus.COMPLETED).scalar() or 0,
        "overdue":     db.query(func.count(Reminder.id)).filter(
            Reminder.due_date < now,
            Reminder.status.in_([ReminderStatus.PENDING, ReminderStatus.IN_PROGRESS])
        ).scalar() or 0,
    }


@router.get("/tickets/stats")
def ticket_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    return {
        "total":       db.query(func.count(Ticket.id)).scalar() or 0,
        "open":        db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.OPEN).scalar() or 0,
        "in_progress": db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.IN_PROGRESS).scalar() or 0,
        "resolved":    db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.RESOLVED).scalar() or 0,
        "closed":      db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.CLOSED).scalar() or 0,
    }


@router.get("/cases/stats")
def case_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    try:
        from app.models.case import Case, CaseStatus       # FIX: correct module
        return {
            "total":   db.query(func.count(Case.id)).scalar() or 0,
            "active":  db.query(func.count(Case.id)).filter(Case.status == CaseStatus.ACTIVE).scalar() or 0,
            "pending": db.query(func.count(Case.id)).filter(Case.status == CaseStatus.PENDING).scalar() or 0,
            "closed":  db.query(func.count(Case.id)).filter(Case.status == CaseStatus.CLOSED).scalar() or 0,
        }
    except Exception:
        return {"total": 0, "active": 0, "pending": 0, "closed": 0}


@router.get("/activity/recent")
def recent_activity(limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    activity = []
    for r in db.query(Reminder).order_by(Reminder.created_at.desc()).limit(limit).all():
        activity.append({"type": "reminder", "id": r.id, "title": r.title,
                         "status": r.status.value if hasattr(r.status, "value") else str(r.status),
                         "created_at": r.created_at.isoformat() if r.created_at else ""})
    for t in db.query(Ticket).order_by(Ticket.created_at.desc()).limit(limit).all():
        activity.append({"type": "ticket", "id": t.id, "title": t.title,
                         "status": t.status.value if hasattr(t.status, "value") else str(t.status),
                         "created_at": t.created_at.isoformat() if t.created_at else ""})
    activity.sort(key=lambda x: x["created_at"], reverse=True)
    return activity[:limit]


@router.get("/trends/weekly")
def weekly_trends(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    start = datetime.utcnow() - timedelta(days=7)
    end   = datetime.utcnow()
    # FIX: Reminder.completed_at doesn't exist — use updated_at + status filter instead
    completed = db.query(func.count(Reminder.id)).filter(
        Reminder.status == ReminderStatus.COMPLETED,
        Reminder.updated_at >= start                        # FIX: was Reminder.completed_at
    ).scalar() or 0
    return {
        "period": "last_7_days", "start_date": start.isoformat(), "end_date": end.isoformat(),
        "new_reminders": db.query(func.count(Reminder.id)).filter(Reminder.created_at >= start).scalar() or 0,
        "new_tickets":   db.query(func.count(Ticket.id)).filter(Ticket.created_at >= start).scalar() or 0,
        "completed_reminders": completed,
    }


@router.get("/performance/user/{user_id}")
def user_performance(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    a_r = db.query(func.count(Reminder.id)).filter(Reminder.assigned_to_id == user_id).scalar() or 0
    c_r = db.query(func.count(Reminder.id)).filter(Reminder.assigned_to_id == user_id, Reminder.status == ReminderStatus.COMPLETED).scalar() or 0
    a_t = db.query(func.count(Ticket.id)).filter(Ticket.assigned_to_id == user_id).scalar() or 0
    r_t = db.query(func.count(Ticket.id)).filter(Ticket.assigned_to_id == user_id, Ticket.status == TicketStatus.RESOLVED).scalar() or 0
    return {
        "user_id": user_id,
        "reminders": {"assigned": a_r, "completed": c_r, "completion_rate": round(c_r/a_r*100,1) if a_r else 0},
        "tickets":   {"assigned": a_t, "resolved":  r_t, "resolution_rate": round(r_t/a_t*100,1) if a_t else 0},
    }
