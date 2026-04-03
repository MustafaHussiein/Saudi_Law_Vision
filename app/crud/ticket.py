"""CRUD operations for tickets"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.ticket import Ticket

def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def get_tickets(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 50) -> List[Ticket]:
    query = db.query(Ticket)
    if user_id:
        query = query.filter((Ticket.created_by_id == user_id) | (Ticket.assigned_to_id == user_id))
    return query.offset(skip).limit(limit).all()