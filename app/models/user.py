"""
User model for authentication and user management
"""

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    LAWYER = "lawyer"
    CLIENT = "client"
    STAFF = "staff"


class User(Base):
    """User model for authentication and profile"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    full_name_ar = Column(String(255), nullable=True)  # Arabic name
    hashed_password = Column(String(255), nullable=False)
    
    role = Column(SQLEnum(UserRole), default=UserRole.CLIENT, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    phone = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Professional info (for lawyers/staff)
    license_number = Column(String(100), nullable=True)  # رقم الترخيص
    specialization = Column(String(255), nullable=True)  # التخصص
    bio = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    created_reminders = relationship("Reminder", back_populates="creator", foreign_keys="Reminder.created_by_id")
    assigned_reminders = relationship("Reminder", back_populates="assigned_to_user", foreign_keys="Reminder.assigned_to_id")
    
    created_tickets = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.created_by_id")
    assigned_tickets = relationship("Ticket", back_populates="assigned_to_user", foreign_keys="Ticket.assigned_to_id")
    
    notifications = relationship("Notification", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"