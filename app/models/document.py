"""
Document model for file management
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class DocumentType(str, enum.Enum):
    """Document type - نوع المستند"""
    CONTRACT = "contract"        # عقد
    COURT_FILING = "court_filing"  # صحيفة دعوى
    EVIDENCE = "evidence"        # دليل
    CORRESPONDENCE = "correspondence"  # مراسلات
    POWER_OF_ATTORNEY = "power_of_attorney"  # وكالة
    ID_DOCUMENT = "id_document"  # وثيقة هوية
    OTHER = "other"              # أخرى


class DocumentStatus(str, enum.Enum):
    """Document status - حالة المستند"""
    DRAFT = "draft"              # مسودة
    PENDING_REVIEW = "pending_review"  # قيد المراجعة
    APPROVED = "approved"        # معتمد
    ARCHIVED = "archived"        # مؤرشف


class Document(Base):
    """
    Document model - نموذج المستند
    For managing uploaded documents
    """
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # File info
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_type = Column(String(50), nullable=True)  # MIME type
    file_extension = Column(String(10), nullable=True)  # .pdf, .docx, etc.
    
    # Classification
    document_type = Column(SQLEnum(DocumentType), default=DocumentType.OTHER, nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False)
    
    # Related entities
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # OCR/Extracted text (for search)
    extracted_text = Column(Text, nullable=True)
    extracted_text_ar = Column(Text, nullable=True)
    
    # Metadata
    tags = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    
    # Version control
    version = Column(Integer, default=1)
    is_latest_version = Column(Boolean, default=True)
    parent_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Security
    is_confidential = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="documents")
    case = relationship("Case", back_populates="documents")
    uploaded_by = relationship("User")
    versions = relationship("Document", backref="parent", remote_side=[id])
    
    def __repr__(self):
        return f"<Document {self.id}: {self.file_name}>"
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0.0