"""
Client Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Base Schema
class ClientBase(BaseModel):
    """Base client schema"""
    full_name: str = Field(..., min_length=1, max_length=200)
    full_name_ar: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100, default="Saudi Arabia")
    national_id: Optional[str] = Field(None, max_length=20)
    passport_number: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=200)
    company_name_ar: Optional[str] = Field(None, max_length=200)
    company_registration: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    notes_ar: Optional[str] = None
    is_active: bool = True


# Create Schema
class ClientCreate(ClientBase):
    """Schema for creating a client"""
    pass


# Update Schema
class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    full_name_ar: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    national_id: Optional[str] = Field(None, max_length=20)
    passport_number: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=200)
    company_name_ar: Optional[str] = Field(None, max_length=200)
    company_registration: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    notes_ar: Optional[str] = None
    is_active: Optional[bool] = None


# Response Schema
class ClientResponse(ClientBase):
    """Schema for client response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# List Response
class ClientListResponse(BaseModel):
    """Schema for paginated client list"""
    total: int
    clients: list[ClientResponse]
    skip: int
    limit: int
