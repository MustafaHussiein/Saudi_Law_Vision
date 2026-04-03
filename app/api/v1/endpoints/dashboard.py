"""Dashboard API - FIXED"""
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus

router = APIRouter()


@router.get("")
def get_dashboard_stats(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_active_user)) -> Any:
    """Dashboard stats - uses TICKETS not reminders"""
    
    if current_user.is_superuser:
        pending = db.query(Ticket).filter(Ticket.status == TicketStatus.PENDING).count()
        in_progress = db.query(Ticket).filter(Ticket.status == TicketStatus.IN_PROGRESS).count()
        open_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).count()
        total_clients = db.query(User).filter(User.role == UserRole.CLIENT).count()
    else:
        pending = db.query(Ticket).filter(
            Ticket.status == TicketStatus.PENDING,
            (Ticket.created_by_id == current_user.id) | (Ticket.assigned_to_id == current_user.id)
        ).count()
        in_progress = db.query(Ticket).filter(
            Ticket.status == TicketStatus.IN_PROGRESS,
            (Ticket.created_by_id == current_user.id) | (Ticket.assigned_to_id == current_user.id)
        ).count()
        open_tickets = db.query(Ticket).filter(
            Ticket.status == TicketStatus.OPEN,
            (Ticket.created_by_id == current_user.id) | (Ticket.assigned_to_id == current_user.id)
        ).count()
        total_clients = db.query(User).filter(User.role == UserRole.CLIENT).count()
    
    return {
        "pending": pending,
        "in_progress": in_progress,
        "waiting": open_tickets,
        "assigned": in_progress,
        "total_clients": total_clients
    }
