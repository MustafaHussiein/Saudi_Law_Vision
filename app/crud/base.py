"""
Base CRUD operations
Generic CRUD class that can be inherited by specific CRUD classes
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations
    
    Type parameters:
        ModelType: SQLAlchemy model
        CreateSchemaType: Pydantic schema for creation
        UpdateSchemaType: Pydantic schema for updates
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with a SQLAlchemy model
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Record or None if not found
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of records
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record
        
        Args:
            db: Database session
            obj_in: Pydantic schema with creation data
            
        Returns:
            Created record
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record
        
        Args:
            db: Database session
            db_obj: Existing database object
            obj_in: Pydantic schema or dict with update data
            
        Returns:
            Updated record
        """
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: int) -> ModelType:
        """
        Delete a record
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Deleted record
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
    
    def count(self, db: Session) -> int:
        """
        Count total records
        
        Args:
            db: Database session
            
        Returns:
            Total count
        """
        return db.query(self.model).count()
    
    def exists(self, db: Session, *, id: int) -> bool:
        """
        Check if record exists
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            True if exists, False otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first() is not None
