"""
Reminder CRUD operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.reminder import Reminder
from app.schemas.reminder import ReminderCreate, ReminderUpdate


def get_reminder(db: Session, reminder_id: int) -> Optional[Reminder]:
    """Get reminder by ID"""
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()


def get_reminders(
    db: Session,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Reminder]:
    """Get list of reminders"""
    query = db.query(Reminder)
    
    if user_id:
        query = query.filter(
            (Reminder.created_by_id == user_id) | (Reminder.assigned_to_id == user_id)
        )
    
    return query.order_by(Reminder.created_at.desc()).offset(skip).limit(limit).all()


def create_reminder(
    db: Session,
    reminder_in: ReminderCreate,
    creator_id: int
) -> Reminder:
    """Create new reminder"""
    from app.utils.hijri_calendar import gregorian_to_hijri
    
    db_reminder = Reminder(
        **reminder_in.model_dump(exclude={'due_date'}),
        created_by_id=creator_id,
        due_date=reminder_in.due_date,
        due_date_hijri=gregorian_to_hijri(reminder_in.due_date.date()) if reminder_in.due_date else None
    )
    
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def update_reminder(
    db: Session,
    reminder: Reminder,
    reminder_in: ReminderUpdate
) -> Reminder:
    """Update reminder"""
    update_data = reminder_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(reminder, field, value)
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def delete_reminder(db: Session, reminder_id: int) -> None:
    """Delete reminder"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if reminder:
        db.delete(reminder)
        db.commit()