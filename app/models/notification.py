"""
Notification model for user notifications and alerts
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification type - نوع الإشعار"""
    REMINDER = "reminder"        # تذكير
    TASK = "task"                # مهمة
    MESSAGE = "message"          # رسالة
    ALERT = "alert"              # تنبيه
    UPDATE = "update"            # تحديث
    SYSTEM = "system"            # نظام


class NotificationPriority(str, enum.Enum):
    """Notification priority - أولوية الإشعار"""
    LOW = "low"          # منخفضة
    NORMAL = "normal"    # عادية
    HIGH = "high"        # عالية
    URGENT = "urgent"    # عاجل


class Notification(Base):
    """
    Notification model - نموذج الإشعار
    For الاشعارات والمهام (Notifications & Tasks)
    """
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic info
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    message = Column(Text, nullable=True)
    message_ar = Column(Text, nullable=True)
    
    # Classification
    notification_type = Column(SQLEnum(NotificationType), default=NotificationType.ALERT, nullable=False)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Related entity (optional)
    related_entity_type = Column(String(50), nullable=True)  # e.g., "reminder", "ticket", "case"
    related_entity_id = Column(Integer, nullable=True)
    
    # Action URL (optional)
    action_url = Column(String(500), nullable=True)  # Link to related page
    
    # Icon/Color (for UI)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} for User {self.user_id}>"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    @property
    def is_urgent(self) -> bool:
        """Check if notification is urgent"""
        return self.priority == NotificationPriority.URGENT