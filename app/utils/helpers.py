"""General Helper Functions"""
import uuid
from typing import Any, Optional

def generate_uuid() -> str:
    """Generate UUID string"""
    return str(uuid.uuid4())

def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """Safely get dict value"""
    return dictionary.get(key, default)

def truncate_string(text: str, length: int = 100, suffix: str = "...") -> str:
    """Truncate string to length"""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix
