"""Tickets API - With type filter for lawyers"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus, TicketType, TicketMessage

router = APIRouter()


class TicketIn(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ticket_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to_id: Optional[int] = None


class MessageIn(BaseModel):
    message: str


def _next_num(db: Session) -> str:
    last = db.query(Ticket).order_by(Ticket.id.desc()).first()
    return f"TKT-{(last.id + 1 if last else 1):06d}"


def _d(t: Ticket) -> dict:
    return {k: (v.value if hasattr(v, "value") else (str(v) if hasattr(v, "isoformat") else v))
            for k, v in t.__dict__.items() if not k.startswith("_")}


@router.get("")
def list_tickets(
    skip: int = 0, 
    limit: int = 50, 
    status_filter: Optional[str] = None,
    type_filter: Optional[str] = None,  # NEW: Filter by ticket type
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    List tickets with filters:
    - status_filter: pending, in_progress, open, closed, resolved
    - type_filter: inquiry, support, complaint, request (استفسار، دعم فني، شكوى، طلب)
    
    Permissions:
    - Admin: sees ALL
    - Lawyer/Employee: sees ONLY assigned to them
    - Client: sees ONLY their own
    """
    q = db.query(Ticket)
    
    # Permission filtering
    if current_user.is_superuser:
        pass  # Admin sees all
    elif current_user.role in [UserRole.LAWYER, UserRole.EMPLOYEE]:
        q = q.filter(
            (Ticket.assigned_to_id == current_user.id) | 
            (Ticket.created_by_id == current_user.id)
        )
    else:
        q = q.filter(Ticket.created_by_id == current_user.id)
    
    # Status filter
    if status_filter:
        status_map = {
            'pending': TicketStatus.PENDING,
            'in_progress': TicketStatus.IN_PROGRESS,
            'open': TicketStatus.OPEN,
            'closed': TicketStatus.CLOSED,
            'resolved': TicketStatus.RESOLVED
        }
        if status_filter.lower() in status_map:
            q = q.filter(Ticket.status == status_map[status_filter.lower()])
    
    # Type filter - NEW
    if type_filter:
        type_map = {
            'inquiry': TicketType.INQUIRY,       # استفسار
            'support': TicketType.SUPPORT,       # دعم فني
            'complaint': TicketType.COMPLAINT,   # شكوى
            'request': TicketType.REQUEST        # طلب
        }
        if type_filter.lower() in type_map:
            q = q.filter(Ticket.ticket_type == type_map[type_filter.lower()])
    
    tickets = q.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": q.count(), "tickets": [_d(t) for t in tickets]}


@router.post("", status_code=201)
def create_ticket(ticket_in: TicketIn, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)) -> Any:
    try:
        ttype = TicketType(ticket_in.ticket_type) if ticket_in.ticket_type else TicketType.SUPPORT
    except ValueError:
        ttype = TicketType.SUPPORT
    
    t = Ticket(
        ticket_number=_next_num(db), title=ticket_in.title, description=ticket_in.description,
        ticket_type=ttype, status=TicketStatus.OPEN, priority=ticket_in.priority or "normal",
        created_by_id=current_user.id, assigned_to_id=ticket_in.assigned_to_id, messages_count=0
    )
    db.add(t); db.commit(); db.refresh(t)
    return _d(t)


@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_active_user)) -> Any:
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t: raise HTTPException(404, "غير موجودة")
    
    # Permission check
    if not current_user.is_superuser:
        if current_user.role in [UserRole.LAWYER, UserRole.EMPLOYEE]:
            if t.assigned_to_id != current_user.id and t.created_by_id != current_user.id:
                raise HTTPException(403, "غير مصرح")
        else:
            if t.created_by_id != current_user.id:
                raise HTTPException(403, "غير مصرح")
    
    result = _d(t)
    result["messages"] = [
        {"id": m.id, "message": m.content, "user_id": m.user_id, "created_at": str(m.created_at)}
        for m in db.query(TicketMessage).filter(TicketMessage.ticket_id == ticket_id).all()
    ]
    return result


@router.put("/{ticket_id}")
def update_ticket(ticket_id: int, ticket_in: TicketIn, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)) -> Any:
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t: raise HTTPException(404, "غير موجودة")
    
    if not current_user.is_superuser:
        if current_user.role in [UserRole.LAWYER, UserRole.EMPLOYEE]:
            if t.assigned_to_id != current_user.id and t.created_by_id != current_user.id:
                raise HTTPException(403, "غير مصرح")
        else:
            if t.created_by_id != current_user.id:
                raise HTTPException(403, "غير مصرح")
    
    for field, value in ticket_in.model_dump(exclude_unset=True, exclude_none=True).items():
        if field == "status" and value:
            status_map = {
                "in_progress": TicketStatus.IN_PROGRESS, "resolved": TicketStatus.RESOLVED,
                "open": TicketStatus.OPEN, "closed": TicketStatus.CLOSED, "pending": TicketStatus.PENDING
            }
            t.status = status_map.get(value.lower(), TicketStatus.OPEN)
        elif field == "ticket_type" and value:
            try: t.ticket_type = TicketType(value)
            except: pass
        else:
            setattr(t, field, value)
    
    db.commit(); db.refresh(t)
    return _d(t)


@router.post("/{ticket_id}/close")
def close_ticket(ticket_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_active_user)) -> Any:
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t: raise HTTPException(404, "غير موجودة")
    
    if not current_user.is_superuser:
        if current_user.role in [UserRole.LAWYER, UserRole.EMPLOYEE]:
            if t.assigned_to_id != current_user.id and t.created_by_id != current_user.id:
                raise HTTPException(403, "غير مصرح")
        else:
            if t.created_by_id != current_user.id:
                raise HTTPException(403, "غير مصرح")
    
    t.status = TicketStatus.CLOSED; t.closed_at = datetime.utcnow()
    db.commit()
    return {"message": "تم", "id": ticket_id}


@router.post("/{ticket_id}/messages", status_code=201)
def add_message(ticket_id: int, msg_in: MessageIn, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_active_user)) -> Any:
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t: raise HTTPException(404, "غير موجودة")
    
    if not current_user.is_superuser:
        if current_user.role in [UserRole.LAWYER, UserRole.EMPLOYEE]:
            if t.assigned_to_id != current_user.id and t.created_by_id != current_user.id:
                raise HTTPException(403, "غير مصرح")
        else:
            if t.created_by_id != current_user.id:
                raise HTTPException(403, "غير مصرح")
    
    msg = TicketMessage(ticket_id=ticket_id, user_id=current_user.id, content=msg_in.message)
    db.add(msg); t.messages_count = (t.messages_count or 0) + 1
    db.commit(); db.refresh(msg)
    return {"id": msg.id, "message": msg.content, "user_id": msg.user_id}


@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)) -> Any:
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t: raise HTTPException(404, "غير موجودة")
    
    if not current_user.is_superuser and t.created_by_id != current_user.id:
        raise HTTPException(403, "فقط المنشئ")
    
    db.delete(t); db.commit()
    return {"message": "تم الحذف", "id": ticket_id}