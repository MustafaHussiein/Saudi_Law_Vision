"""
Case Model - Legal Cases
"""

from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class CaseStatus(enum.Enum):
    """Case status enum"""
    PENDING = "pending"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    CLOSED = "closed"
    WON = "won"
    LOST = "lost"
    SETTLED = "settled"


class CaseType(enum.Enum):
    """Case type enum"""
    CIVIL = "civil"
    CRIMINAL = "criminal"
    COMMERCIAL = "commercial"
    FAMILY = "family"
    LABOR = "labor"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


class Case(BaseModel):
    """Legal case model"""
    
    __tablename__ = "cases"
    
    # Basic info
    case_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500))
    description = Column(Text)
    description_ar = Column(Text)
    
    # Case details
    case_type = Column(SQLEnum(CaseType), nullable=False)
    status = Column(SQLEnum(CaseStatus), default=CaseStatus.PENDING, nullable=False)
    
    # Dates
    filing_date = Column(Date)
    filing_date_hijri = Column(String(20))
    closing_date = Column(Date)
    next_hearing_date = Column(Date)
    
    # Relations
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="cases")
    
    lawyer_id = Column(Integer, ForeignKey("users.id"))
    lawyer = relationship("User", foreign_keys=[lawyer_id])
    
    # Court information
    court_name = Column(String(200))
    court_name_ar = Column(String(200))
    judge_name = Column(String(200))
    judge_name_ar = Column(String(200))
    case_number_at_court = Column(String(100))
    
    # Financial
    estimated_value = Column(Integer)
    actual_value = Column(Integer)
    fees_charged = Column(Integer)
    expenses = Column(Integer)
    
    # Additional info
    priority = Column(String(20), default="normal")
    is_confidential = Column(Boolean, default=False)
    notes = Column(Text)
    notes_ar = Column(Text)
    
    # Relationships
    hearings = relationship("Hearing", back_populates="case", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="case")
    invoices = relationship("Invoice", back_populates="case")
    
    def __repr__(self):
        return f"<Case(id={self.id}, number={self.case_number}, title={self.title})>"


class Hearing(BaseModel):
    """Court hearing/session"""
    
    __tablename__ = "hearings"
    
    # Hearing details
    hearing_date = Column(Date, nullable=False)
    hearing_date_hijri = Column(String(20))
    hearing_time = Column(String(10))
    
    title = Column(String(200))
    title_ar = Column(String(200))
    description = Column(Text)
    description_ar = Column(Text)
    
    # Location
    location = Column(String(300))
    location_ar = Column(String(300))
    courtroom = Column(String(100))
    
    # Status
    status = Column(String(50), default="scheduled")  # scheduled, completed, postponed, cancelled
    outcome = Column(Text)
    outcome_ar = Column(Text)
    
    # Relations
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    case = relationship("Case", back_populates="hearings")
    
    # Attendees
    attended_by = Column(Text)  # JSON list of attendees
    
    # Next steps
    next_hearing_date = Column(Date)
    action_items = Column(Text)
    action_items_ar = Column(Text)
    
    def __repr__(self):
        return f"<Hearing(id={self.id}, date={self.hearing_date}, case_id={self.case_id})>"
