"""
File handling utilities
Upload, download, and manage files
"""

import os
import uuid
from typing import Optional
from pathlib import Path
from fastapi import UploadFile, HTTPException

from app.core.constants import (
    MAX_UPLOAD_SIZE,
    ALLOWED_DOCUMENT_EXTENSIONS,
    ALLOWED_IMAGE_EXTENSIONS,
    DOCUMENTS_DIR,
    IMAGES_DIR
)


def validate_file_size(file: UploadFile, max_size: int = MAX_UPLOAD_SIZE) -> bool:
    """
    Validate file size
    
    Args:
        file: Uploaded file
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If file is too large
    """
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {max_size / 1024 / 1024:.1f}MB"
        )
    
    return True


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Validate file extension
    
    Args:
        filename: File name
        allowed_extensions: Set of allowed extensions
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If extension not allowed
    """
    ext = Path(filename).suffix.lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    return True


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate unique filename
    
    Args:
        original_filename: Original file name
        
    Returns:
        Unique filename
    """
    ext = Path(original_filename).suffix
    unique_name = f"{uuid.uuid4()}{ext}"
    return unique_name


async def save_upload_file(
    file: UploadFile,
    destination_dir: str,
    allowed_extensions: set = ALLOWED_DOCUMENT_EXTENSIONS
) -> str:
    """
    Save uploaded file
    
    Args:
        file: Uploaded file
        destination_dir: Directory to save file
        allowed_extensions: Allowed file extensions
        
    Returns:
        Saved file path
    """
    # Validate
    validate_file_size(file)
    validate_file_extension(file.filename, allowed_extensions)
    
    # Create directory if not exists
    os.makedirs(destination_dir, exist_ok=True)
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename)
    file_path = os.path.join(destination_dir, filename)
    
    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return file_path


def delete_file(file_path: str) -> bool:
    """
    Delete file
    
    Args:
        file_path: Path to file
        
    Returns:
        True if deleted
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
