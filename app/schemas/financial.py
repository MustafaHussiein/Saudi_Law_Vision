"""
Financial Pydantic schemas
"""

from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.base import TimestampSchema


# Invoice Schemas
class InvoiceBase(BaseModel):
    """Base invoice schema"""
    amount: Decimal = Field(..., gt=0, description="Invoice amount")
    tax_amount: Decimal = Field(default=0, ge=0)
    currency: str = Field(default="SAR", max_length=3)
    issue_date: date
    due_date: date
    client_id: int
    case_id: Optional[int] = None
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    """Schema for creating invoice"""
    pass


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice"""
    amount: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class InvoiceResponse(InvoiceBase, TimestampSchema):
    """Schema for invoice response"""
    invoice_number: str
    total_amount: Decimal
    status: str
    paid_date: Optional[date] = None


# Payment Schemas
class PaymentBase(BaseModel):
    """Base payment schema"""
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="SAR", max_length=3)
    payment_method: str
    payment_date: date
    invoice_id: int
    client_id: int
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Schema for creating payment"""
    pass


class PaymentResponse(PaymentBase, TimestampSchema):
    """Schema for payment response"""
    payment_number: str
    status: str
