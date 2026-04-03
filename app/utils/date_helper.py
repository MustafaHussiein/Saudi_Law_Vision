"""
Date and time utilities
Including Hijri calendar support
"""

from datetime import datetime, date, timedelta
from typing import Optional

try:
    from hijri_converter import Hijri, Gregorian
    HIJRI_AVAILABLE = True
except ImportError:
    HIJRI_AVAILABLE = False


def gregorian_to_hijri(gregorian_date: date) -> Optional[str]:
    """
    Convert Gregorian date to Hijri
    
    Args:
        gregorian_date: Gregorian date
        
    Returns:
        Hijri date string (YYYY-MM-DD format) or None if library not available
    """
    if not HIJRI_AVAILABLE:
        return None
    
    try:
        hijri = Gregorian(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day
        ).to_hijri()
        
        return f"{hijri.year}-{hijri.month:02d}-{hijri.day:02d}"
    except:
        return None


def hijri_to_gregorian(hijri_date_str: str) -> Optional[date]:
    """
    Convert Hijri date to Gregorian
    
    Args:
        hijri_date_str: Hijri date string (YYYY-MM-DD format)
        
    Returns:
        Gregorian date or None if library not available
    """
    if not HIJRI_AVAILABLE:
        return None
    
    try:
        year, month, day = map(int, hijri_date_str.split('-'))
        gregorian = Hijri(year, month, day).to_gregorian()
        return date(gregorian.year, gregorian.month, gregorian.day)
    except:
        return None


def format_date_arabic(dt: datetime) -> str:
    """
    Format date in Arabic style
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted Arabic date string
    """
    months_ar = [
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    ]
    
    return f"{dt.day} {months_ar[dt.month - 1]} {dt.year}"


def get_days_until(target_date: date) -> int:
    """
    Get number of days until target date
    
    Args:
        target_date: Target date
        
    Returns:
        Number of days (negative if past)
    """
    today = date.today()
    delta = target_date - today
    return delta.days


def is_overdue(target_date: date) -> bool:
    """
    Check if date is overdue
    
    Args:
        target_date: Target date
        
    Returns:
        True if overdue
    """
    return target_date < date.today()
