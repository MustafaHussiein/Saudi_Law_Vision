"""
Reminder Pydantic schemas
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.reminder import ReminderStatus, ReminderPriority


class ReminderBase(BaseModel):
    title: str
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    status: ReminderStatus = ReminderStatus.PENDING
    priority: ReminderPriority = ReminderPriority.NORMAL
    due_date: Optional[datetime] = None


class ReminderCreate(ReminderBase):
    assigned_to_id: Optional[int] = None
    client_id: Optional[int] = None


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ReminderStatus] = None
    priority: Optional[ReminderPriority] = None
    assigned_to_id: Optional[int] = None


class ReminderResponse(ReminderBase):
    id: int
    created_by_id: int
    assigned_to_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True