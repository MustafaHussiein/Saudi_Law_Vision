"""Notification CRUD"""
from typing import List
from sqlalchemy.orm import Session
from app.models.notification import Notification

def get_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).offset(skip).limit(limit).all()