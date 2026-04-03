"""
Database models for Legal Tech Platform
This file exports all models so they can be imported from app.models
"""

# Import all models
from app.models.user import User, UserRole
from app.models.reminder import Reminder, ReminderComment, ReminderStatus, ReminderPriority
from app.models.ticket import Ticket, TicketMessage, TicketStatus, TicketType
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.client import Client, Case, Hearing, CaseStatus, CaseType
from app.models.document import Document, DocumentType, DocumentStatus

# Export all models and enums
__all__ = [
    # User
    "User",
    "UserRole",
    
    # Reminder
    "Reminder",
    "ReminderComment",
    "ReminderStatus",
    "ReminderPriority",
    
    # Ticket
    "Ticket",
    "TicketMessage",
    "TicketStatus",
    "TicketType",
    
    # Notification
    "Notification",
    "NotificationType",
    "NotificationPriority",
    
    # Client & Case
    "Client",
    "Case",
    "Hearing",
    "CaseStatus",
    "CaseType",
    
    # Document
    "Document",
    "DocumentType",
    "DocumentStatus",
]