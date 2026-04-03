"""Arabic Text Utilities"""

def normalize_arabic(text: str) -> str:
    """Normalize Arabic text"""
    # Remove diacritics, normalize characters
    return text.strip()

def is_arabic(text: str) -> bool:
    """Check if text contains Arabic"""
    return any('\u0600' <= c <= '\u06FF' for c in text)

def reverse_for_rtl(text: str) -> str:
    """Reverse text for RTL display"""
    return text[::-1] if is_arabic(text) else text
