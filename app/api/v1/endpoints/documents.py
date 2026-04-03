"""Documents API - Fixed PDF download"""
import os, uuid
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User, UserRole
from app.models.document import Document, DocumentStatus

router = APIRouter()
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED = {".pdf",".doc",".docx",".txt",".jpg",".jpeg",".png",".xlsx",".xls"}


def _int_or_none(val) -> Optional[int]:
    if val is None or str(val).strip() == "":
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

def _d(doc: Document, db: Session) -> dict:
    """Convert document to dict WITH uploader info"""
    result = {k: (v.value if hasattr(v, "value") else (str(v) if hasattr(v, "isoformat") else v))
              for k, v in doc.__dict__.items() if not k.startswith("_")}
    
    uploader = db.query(User).filter(User.id == doc.uploaded_by_id).first()
    result["owner_name"] = uploader.full_name_ar or uploader.full_name if uploader else "غير معروف"
    
    if not result.get("file_extension") and doc.file_name:
        result["file_extension"] = os.path.splitext(doc.file_name)[1].lower()
        
    return result

@router.get("")
def list_documents(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_active_user)) -> Any:
    query = db.query(Document)
    if current_user.role == UserRole.CLIENT:
        query = query.filter(Document.uploaded_by_id == current_user.id)
    
    docs = query.order_by(Document.created_at.desc()).all()
    return {"documents": [_d(d, db) for d in docs]}


@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...), title: str = Form(...), description: str = Form(""),
    document_type: str = Form("other"), client_id: Optional[str] = Form(None),
    case_id: Optional[str] = Form(None), is_confidential: Optional[str] = Form("false"),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
) -> Any:
    client_id_int = _int_or_none(client_id)
    case_id_int = _int_or_none(case_id)
    confidential = str(is_confidential).lower() in ("true", "1", "yes", "on")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED:
        raise HTTPException(400, detail=f"نوع الملف غير مدعوم")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(413, detail="حجم الملف أكبر من 50MB")

    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        doc = Document(
            title=title, description=description or None, document_type=document_type,
            file_name=file.filename, file_path=file_path, file_size=len(content),
            file_extension=ext, client_id=client_id_int, case_id=case_id_int,
            is_confidential=confidential, uploaded_by_id=current_user.id,
            status=DocumentStatus.APPROVED,
        )
        db.add(doc); db.commit(); db.refresh(doc)
        return _d(doc, db)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        db.rollback()
        raise HTTPException(500, detail=f"خطأ: {str(e)}")


@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_active_user)) -> Any:
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "المستند غير موجود")
    
    if current_user.role == UserRole.CLIENT:
        if doc.uploaded_by_id != current_user.id:
            raise HTTPException(403, "غير مصرح")
    
    return _d(doc, db)


@router.get("/{doc_id}/download")
async def download_document(doc_id: int, request: Request, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Download document - returns raw bytes for blob consumption
    FIX: Proper content type and headers for PDFs
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "المستند غير موجود")
    
    if current_user.role == UserRole.CLIENT:
        if doc.uploaded_by_id != current_user.id:
            raise HTTPException(403, "غير مصرح")
    
    if not os.path.exists(doc.file_path):
        raise HTTPException(404, "الملف غير موجود")
    
    # Determine MIME type
    ext = doc.file_extension.lower() if doc.file_extension else ''
    mime_types = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp',
        '.txt': 'text/plain', '.md': 'text/markdown',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }
    media_type = mime_types.get(ext, 'application/octet-stream')
    
    # Read file content
    with open(doc.file_path, 'rb') as f:
        content = f.read()
    
    # Return with proper headers for blob consumption
    return Response(
        content=content,
        media_type=media_type,
        headers={
            'Content-Disposition': f'inline; filename="{doc.file_name}"',
            'Cache-Control': 'no-cache'
        }
    )


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)) -> Any:
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "المستند غير موجود")
    
    if not current_user.is_superuser and doc.uploaded_by_id != current_user.id:
        raise HTTPException(403, "فقط من رفع الملف يمكنه حذفه")
    
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc); db.commit()
    return {"message": "تم الحذف", "id": doc_id}