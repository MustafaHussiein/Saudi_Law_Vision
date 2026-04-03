"""
Ticket Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# Base Schema
class TicketBase(BaseModel):
    """Base ticket schema"""
    title: str = Field(..., min_length=1, max_length=300)
    title_ar: Optional[str] = Field(None, max_length=300)
    description: str = Field(..., min_length=1)
    description_ar: Optional[str] = None
    ticket_type: str = Field(..., max_length=50)
    priority: str = Field(default="normal", max_length=20)


# Create Schema
class TicketCreate(TicketBase):
    """Schema for creating a ticket"""
    client_id: Optional[int] = None
    case_id: Optional[int] = None


# Update Schema
class TicketUpdate(BaseModel):
    """Schema for updating a ticket"""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    title_ar: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    assigned_to_id: Optional[int] = None


# Response Schema
class TicketResponse(TicketBase):
    """Schema for ticket response"""
    id: int
    ticket_number: str
    status: str
    created_by_id: int
    assigned_to_id: Optional[int] = None
    client_id: Optional[int] = None
    case_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Message Schema
class TicketMessageBase(BaseModel):
    """Base ticket message schema"""
    message: str = Field(..., min_length=1)
    message_ar: Optional[str] = None


class TicketMessageCreate(TicketMessageBase):
    """Schema for creating ticket message"""
    ticket_id: int


class TicketMessageResponse(TicketMessageBase):
    """Schema for ticket message response"""
    id: int
    ticket_id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
