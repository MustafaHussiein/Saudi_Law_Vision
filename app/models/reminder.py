"""
Reminder/Alert model for task management
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ReminderStatus(str, enum.Enum):
    """Reminder status enumeration - حالة التذكير"""
    PENDING = "pending"          # معلقة
    IN_PROGRESS = "in_progress"  # قيد المعالجة
    ASSIGNED = "assigned"        # تم الأسناد
    WAITING = "waiting"          # قيد الانتظار
    COMPLETED = "completed"      # مكتملة
    CANCELLED = "cancelled"      # ملغاة


class ReminderPriority(str, enum.Enum):
    """Reminder priority - الأولوية"""
    LOW = "low"          # منخفضة
    NORMAL = "normal"    # عادية
    HIGH = "high"        # عالية
    URGENT = "urgent"    # عاجل


class Reminder(Base):
    """
    Reminder/Alert model - نموذج التذكير/التنبيه
    Used for managing reminders, alerts, and tasks
    """
    
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)  # Arabic title
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Status and priority
    status = Column(SQLEnum(ReminderStatus), default=ReminderStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(ReminderPriority), default=ReminderPriority.NORMAL, nullable=False)
    
    # Assignment
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Related entities
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    
    # Timing
    due_date = Column(DateTime, nullable=True)  # تاريخ الاستحقاق
    due_date_hijri = Column(String(50), nullable=True)  # التاريخ الهجري
    reminder_time = Column(DateTime, nullable=True)  # وقت التذكير
    
    # Metadata
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    category = Column(String(100), nullable=True)  # فئة
    
    # Comments/Messages count
    comments_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_reminders", foreign_keys=[created_by_id])
    assigned_to_user = relationship("User", back_populates="assigned_reminders", foreign_keys=[assigned_to_id])
    client = relationship("Client", back_populates="reminders")
    case = relationship("Case", back_populates="reminders")
    comments = relationship("ReminderComment", back_populates="reminder", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Reminder {self.id}: {self.title}>"
    
    @property
    def is_urgent(self) -> bool:
        """Check if reminder is urgent"""
        return self.priority == ReminderPriority.URGENT
    
    @property
    def is_overdue(self) -> bool:
        """Check if reminder is overdue"""
        if self.due_date and self.status not in [ReminderStatus.COMPLETED, ReminderStatus.CANCELLED]:
            return datetime.utcnow() > self.due_date
        return False


class ReminderComment(Base):
    """Comments on reminders - تعليقات على التذكيرات"""
    
    __tablename__ = "reminder_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(Integer, ForeignKey("reminders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    content_ar = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reminder = relationship("Reminder", back_populates="comments")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ReminderComment {self.id} on Reminder {self.reminder_id}>"