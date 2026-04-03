"""
Base model for all SQLAlchemy models
Provides common columns and functionality
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

from app.core.database import Base as SQLAlchemyBase


class BaseModel(SQLAlchemyBase):
    """
    Base model with common columns
    All models should inherit from this
    """
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @declared_attr
    def __tablename__(cls):
        """
        Automatically generate table name from class name
        """
        return cls.__name__.lower()
    
    def dict(self):
        """
        Convert model to dictionary
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        """
        String representation
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
