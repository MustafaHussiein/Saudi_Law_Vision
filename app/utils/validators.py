"""
Input validation utilities
"""

import re
from typing import Optional
from app.core.constants import EMAIL_REGEX, PHONE_REGEX, SAUDI_NATIONAL_ID_REGEX


def validate_email(email: str) -> bool:
    """Validate email format"""
    return bool(re.match(EMAIL_REGEX, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    return bool(re.match(PHONE_REGEX, phone))


def validate_saudi_id(national_id: str) -> bool:
    """Validate Saudi national ID format"""
    return bool(re.match(SAUDI_NATIONAL_ID_REGEX, national_id))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    return True, None
