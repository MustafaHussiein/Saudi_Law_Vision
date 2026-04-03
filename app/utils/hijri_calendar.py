"""Hijri Calendar Utilities"""
from datetime import date
from typing import Optional

try:
    from hijri_converter import Hijri, Gregorian
    HIJRI_AVAILABLE = True
except ImportError:
    HIJRI_AVAILABLE = False

def gregorian_to_hijri_str(greg_date: date) -> Optional[str]:
    """Convert Gregorian to Hijri string"""
    if not HIJRI_AVAILABLE:
        return None
    try:
        h = Gregorian(greg_date.year, greg_date.month, greg_date.day).to_hijri()
        return f"{h.year}/{h.month:02d}/{h.day:02d}"
    except:
        return None

def get_hijri_month_name(month: int) -> str:
    """Get Hijri month name in Arabic"""
    months = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى",
              "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
    return months[month - 1] if 1 <= month <= 12 else ""
