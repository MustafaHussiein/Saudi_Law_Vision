"""Format Utilities"""
from datetime import datetime, date
from decimal import Decimal

def format_currency(amount: Decimal, currency: str = "SAR") -> str:
    """Format currency"""
    return f"{amount:,.2f} {currency}"

def format_date_ar(dt: date) -> str:
    """Format date in Arabic"""
    months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
              "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    return f"{dt.day} {months[dt.month - 1]} {dt.year}"

def format_phone(phone: str) -> str:
    """Format phone number"""
    return phone.strip().replace(" ", "")
