"""
Custom exceptions for the Legal Tech Platform
"""

from typing import Any, Optional, Dict
from fastapi import HTTPException, status


class LegalTechException(Exception):
    """Base exception for Legal Tech Platform"""
    
    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(LegalTechException):
    """Exception raised when a resource is not found"""
    
    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID {resource_id} not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedException(LegalTechException):
    """Exception raised for authentication failures"""
    
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenException(LegalTechException):
    """Exception raised when user lacks permissions"""
    
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class BadRequestException(LegalTechException):
    """Exception raised for invalid requests"""
    
    def __init__(self, message: str = "Bad request", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class ConflictException(LegalTechException):
    """Exception raised when resource already exists"""
    
    def __init__(self, resource: str = "Resource", message: str = None):
        if not message:
            message = f"{resource} already exists"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )


class ValidationException(LegalTechException):
    """Exception raised for validation errors"""
    
    def __init__(self, message: str = "Validation error", errors: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors} if errors else {}
        )


class DatabaseException(LegalTechException):
    """Exception raised for database errors"""
    
    def __init__(self, message: str = "Database error", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class FileUploadException(LegalTechException):
    """Exception raised for file upload errors"""
    
    def __init__(self, message: str = "File upload failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class RateLimitException(LegalTechException):
    """Exception raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Too many requests"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class ServiceUnavailableException(LegalTechException):
    """Exception raised when service is unavailable"""
    
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


# Specific domain exceptions

class ClientNotFoundException(NotFoundException):
    """Client not found"""
    def __init__(self, client_id: int):
        super().__init__("Client", client_id)


class CaseNotFoundException(NotFoundException):
    """Case not found"""
    def __init__(self, case_id: int):
        super().__init__("Case", case_id)


class DocumentNotFoundException(NotFoundException):
    """Document not found"""
    def __init__(self, document_id: int):
        super().__init__("Document", document_id)


class ReminderNotFoundException(NotFoundException):
    """Reminder not found"""
    def __init__(self, reminder_id: int):
        super().__init__("Reminder", reminder_id)


class TicketNotFoundException(NotFoundException):
    """Ticket not found"""
    def __init__(self, ticket_id: int):
        super().__init__("Ticket", ticket_id)


class UserNotFoundException(NotFoundException):
    """User not found"""
    def __init__(self, user_id: int):
        super().__init__("User", user_id)


class InvalidCredentialsException(UnauthorizedException):
    """Invalid login credentials"""
    def __init__(self):
        super().__init__("Invalid email or password")


class TokenExpiredException(UnauthorizedException):
    """JWT token has expired"""
    def __init__(self):
        super().__init__("Token has expired")


class EmailAlreadyExistsException(ConflictException):
    """Email already registered"""
    def __init__(self, email: str):
        super().__init__("User", f"Email {email} already registered")


class DuplicateResourceException(ConflictException):
    """Duplicate resource"""
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(resource, f"{resource} with {field} '{value}' already exists")


# Helper function to convert exceptions to HTTP exceptions
def to_http_exception(exc: LegalTechException) -> HTTPException:
    """
    Convert custom exception to FastAPI HTTPException
    
    Args:
        exc: Custom exception
        
    Returns:
        HTTPException: FastAPI HTTP exception
    """
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            **exc.details
        }
    )
