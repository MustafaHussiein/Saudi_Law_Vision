"""
Document Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# Base Schema
class DocumentBase(BaseModel):
    """Base document schema"""
    title: str = Field(..., min_length=1, max_length=300)
    title_ar: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    document_type: str = Field(..., max_length=50)
    client_id: Optional[int] = None
    case_id: Optional[int] = None
    is_confidential: bool = False
    tags: Optional[str] = None  # JSON array


# Create Schema
class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    file_name: str
    file_path: str
    file_size: int
    file_extension: str


# Update Schema
class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    title_ar: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    document_type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    is_confidential: Optional[bool] = None
    tags: Optional[str] = None


# Response Schema
class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    file_name: str
    file_path: str
    file_size: int
    file_extension: str
    status: str
    uploaded_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Upload Response
class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    id: int
    file_name: str
    file_path: str
    message: str = "File uploaded successfully"
