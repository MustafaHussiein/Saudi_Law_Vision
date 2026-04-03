"""Document CRUD"""
from typing import List
from sqlalchemy.orm import Session
from app.models.document import Document

def get_documents(db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
    return db.query(Document).offset(skip).limit(limit).all()