"""
Financial Models
Invoicing, payments, and financial tracking
"""

from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class InvoiceStatus(enum.Enum):
    """Invoice status"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentStatus(enum.Enum):
    """Payment status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(enum.Enum):
    """Payment methods"""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    ONLINE = "online"


class Invoice(BaseModel):
    """Invoice for legal services"""
    
    __tablename__ = "invoices"
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="SAR")
    
    # Dates
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date)
    
    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    
    # Relations
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="invoices")
    
    case_id = Column(Integer, ForeignKey("cases.id"))
    case = relationship("Case", back_populates="invoices")
    
    # Line items (stored as JSON for simplicity)
    items = Column(Text)  # JSON array of line items
    
    # Notes
    notes = Column(Text)
    notes_ar = Column(Text)
    
    # Payments
    payments = relationship("Payment", back_populates="invoice")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number={self.invoice_number}, amount={self.total_amount})>"


class Payment(BaseModel):
    """Payment record"""
    
    __tablename__ = "payments"
    
    # Payment details
    payment_number = Column(String(50), unique=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="SAR")
    
    # Method and status
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Date
    payment_date = Column(Date, nullable=False)
    
    # Relations
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    invoice = relationship("Invoice", back_populates="payments")
    
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="payments")
    
    # Details
    reference_number = Column(String(100))  # Bank reference, check number, etc.
    notes = Column(Text)
    notes_ar = Column(Text)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, method={self.payment_method.value})>"
