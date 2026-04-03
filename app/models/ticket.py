"""
Ticket model for support and requests
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class TicketStatus(str, enum.Enum):
    """Ticket status - حالة التذكرة"""
    OPEN = "open"                # مفتوحة
    IN_PROGRESS = "in_progress"  # قيد المعالجة
    PENDING = "pending"          # معلقة
    RESOLVED = "resolved"        # تم الحل
    CLOSED = "closed"            # مغلقة


class TicketType(str, enum.Enum):
    """Ticket type - نوع التذكرة"""
    SUPPORT = "support"      # دعم فني
    REQUEST = "request"      # طلب
    COMPLAINT = "complaint"  # شكوى
    INQUIRY = "inquiry"      # استفسار
    OTHER = "other"          # أخرى


class Ticket(Base):
    """
    Ticket model for support and requests - نموذج التذاكر
    """
    
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)  # e.g., TCK-2026-0001
    
    # Basic info
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    description = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=True)
    
    # Classification
    ticket_type = Column(SQLEnum(TicketType), default=TicketType.REQUEST, nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    
    # Assignment
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Related
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    
    # Priority
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Metadata
    tags = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    
    # Messages count
    messages_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_tickets", foreign_keys=[created_by_id])
    assigned_to_user = relationship("User", back_populates="assigned_tickets", foreign_keys=[assigned_to_id])
    client = relationship("Client", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket {self.ticket_number}: {self.title}>"


class TicketMessage(Base):
    """Messages in tickets - رسائل التذاكر"""
    
    __tablename__ = "ticket_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    content_ar = Column(Text, nullable=True)
    
    is_internal = Column(Boolean, default=False)  # Internal note vs public message
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="messages")
    user = relationship("User")
    
    def __repr__(self):
        return f"<TicketMessage {self.id} in Ticket {self.ticket_id}>"