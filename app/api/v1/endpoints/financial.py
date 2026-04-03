"""Financial API endpoints - Placeholder"""
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/overview")
def get_financial_overview(db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_active_user)) -> Any:
    return {"total_revenue": 0, "pending_payments": 0, "paid_invoices": 0}


@router.get("/invoices")
def list_invoices(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    return {"total": 0, "invoices": []}


@router.get("/payments")
def list_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Any:
    return {"total": 0, "payments": []}
