"""
Client, Case, and Hearing models
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class Client(Base):
    """Client model - نموذج العميل"""
    
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    full_name = Column(String(255), nullable=False)
    full_name_ar = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(50), nullable=True)
    phone_secondary = Column(String(50), nullable=True)
    
    # Identification
    national_id = Column(String(50), nullable=True)  # رقم الهوية
    passport_number = Column(String(50), nullable=True)  # رقم الجواز
    
    # Address
    address = Column(Text, nullable=True)
    address_ar = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Company (if applicable)
    company_name = Column(String(255), nullable=True)
    company_name_ar = Column(String(255), nullable=True)
    company_registration = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cases = relationship("Case", back_populates="client")
    reminders = relationship("Reminder", back_populates="client")
    tickets = relationship("Ticket", back_populates="client")
    documents = relationship("Document", back_populates="client")
    
    def __repr__(self):
        return f"<Client {self.id}: {self.full_name}>"


class CaseStatus(str, enum.Enum):
    """Case status - حالة القضية"""
    ACTIVE = "active"        # نشطة
    PENDING = "pending"      # معلقة
    CLOSED = "closed"        # مغلقة
    ARCHIVED = "archived"    # مؤرشفة


class CaseType(str, enum.Enum):
    """Case type - نوع القضية"""
    CIVIL = "civil"              # مدنية
    CRIMINAL = "criminal"        # جنائية
    COMMERCIAL = "commercial"    # تجارية
    FAMILY = "family"            # أحوال شخصية
    LABOR = "labor"              # عمالية
    ADMINISTRATIVE = "administrative"  # إدارية
    OTHER = "other"              # أخرى


class Case(Base):
    """Legal case model - نموذج القضية القانونية"""
    
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), unique=True, index=True, nullable=False)  # رقم القضية
    
    # Basic info
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Classification
    case_type = Column(SQLEnum(CaseType), nullable=False)
    status = Column(SQLEnum(CaseStatus), default=CaseStatus.ACTIVE, nullable=False)
    
    # Court information
    court_name = Column(String(255), nullable=True)  # اسم المحكمة
    court_name_ar = Column(String(255), nullable=True)
    judge_name = Column(String(255), nullable=True)  # اسم القاضي
    judge_name_ar = Column(String(255), nullable=True)
    
    # Dates
    filing_date = Column(DateTime, nullable=True)  # تاريخ رفع الدعوى
    filing_date_hijri = Column(String(50), nullable=True)
    next_hearing_date = Column(DateTime, nullable=True)  # تاريخ الجلسة القادمة
    next_hearing_date_hijri = Column(String(50), nullable=True)
    closing_date = Column(DateTime, nullable=True)  # تاريخ إغلاق القضية
    
    # Related parties
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    lawyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # المحامي المسؤول
    
    # Opposing party
    opposing_party = Column(String(255), nullable=True)  # الطرف الآخر
    opposing_party_ar = Column(String(255), nullable=True)
    opposing_lawyer = Column(String(255), nullable=True)  # محامي الطرف الآخر
    
    # Financial
    claim_amount = Column(Integer, nullable=True)  # قيمة المطالبة
    currency = Column(String(10), default="SAR")
    
    # Notes
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="cases")
    lawyer = relationship("User")
    reminders = relationship("Reminder", back_populates="case")
    documents = relationship("Document", back_populates="case")
    hearings = relationship("Hearing", back_populates="case")
    
    def __repr__(self):
        return f"<Case {self.case_number}: {self.title}>"


class Hearing(Base):
    """Court hearing - جلسة محكمة"""
    
    __tablename__ = "hearings"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    
    hearing_date = Column(DateTime, nullable=False)
    hearing_date_hijri = Column(String(50), nullable=True)
    
    location = Column(String(255), nullable=True)  # مكان الجلسة
    location_ar = Column(String(255), nullable=True)
    
    outcome = Column(Text, nullable=True)  # نتيجة الجلسة
    outcome_ar = Column(Text, nullable=True)
    
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    case = relationship("Case", back_populates="hearings")
    
    def __repr__(self):
        return f"<Hearing {self.id} for Case {self.case_id}>"