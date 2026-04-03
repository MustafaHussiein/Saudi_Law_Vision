"""Clients API - Shows ALL from Client table (not User table)"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.client import Client

router = APIRouter()


class ClientIn(BaseModel):
    full_name: str
    full_name_ar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    phone_secondary: Optional[str] = None
    national_id: Optional[str] = None
    passport_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "Saudi Arabia"
    company_name: Optional[str] = None
    company_name_ar: Optional[str] = None
    company_registration: Optional[str] = None
    notes: Optional[str] = None
    notes_ar: Optional[str] = None
    is_active: bool = True


def _d(c: Client) -> dict:
    return {k: (str(v) if hasattr(v, "isoformat") else v)
            for k, v in c.__dict__.items() if not k.startswith("_")}


@router.get("")
def list_clients(skip: int = 0, limit: int = 100, search: Optional[str] = None,
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    """
    List ALL clients from Client table
    NOTE: This is SEPARATE from users with role=client
    """
    q = db.query(Client)
    
    if search:
        q = q.filter(
            (Client.full_name.contains(search)) | 
            (Client.full_name_ar.contains(search)) |
            (Client.email.contains(search)) |
            (Client.phone.contains(search))
        )
    
    total = q.count()
    clients = q.order_by(Client.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "clients": [_d(c) for c in clients]}


@router.post("", status_code=201)
def create_client(client_in: ClientIn, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)) -> Any:
    if client_in.email:
        if db.query(Client).filter(Client.email == client_in.email).first():
            raise HTTPException(409, detail=f"البريد {client_in.email} مسجل بالفعل")
    
    try:
        client = Client(**client_in.model_dump())
        db.add(client); db.commit(); db.refresh(client)
        return _d(client)
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "بيانات مكررة")
    except Exception as e:
        db.rollback(); raise HTTPException(500, str(e))


@router.get("/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_active_user)) -> Any:
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c: raise HTTPException(404, "العميل غير موجود")
    return _d(c)


@router.put("/{client_id}")
def update_client(client_id: int, client_in: ClientIn, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)) -> Any:
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c: raise HTTPException(404, "العميل غير موجود")
    
    if client_in.email and client_in.email != c.email:
        if db.query(Client).filter(Client.email == client_in.email, Client.id != client_id).first():
            raise HTTPException(409, "البريد مسجل بالفعل")
    
    try:
        for k, v in client_in.model_dump(exclude_unset=True).items():
            setattr(c, k, v)
        db.commit(); db.refresh(c)
        return _d(c)
    except Exception as e:
        db.rollback(); raise HTTPException(500, str(e))


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)) -> Any:
    c = db.query(Client).filter(Client.id == client_id).first()
    if not c: raise HTTPException(404, "العميل غير موجود")
    db.delete(c); db.commit()
    return {"message": "تم الحذف", "id": client_id}