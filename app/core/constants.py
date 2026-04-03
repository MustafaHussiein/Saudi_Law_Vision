"""
Application constants
Centralized place for all constant values used across the application
"""

from enum import Enum


# ==================== API SETTINGS ====================

API_VERSION = "1.0.0"
API_TITLE = "Legal Tech Platform - Riada Law"
API_DESCRIPTION = """
Legal Tech Platform API for law firm management

## Features

* **Authentication**: JWT-based authentication
* **Clients**: Manage clients and their information
* **Cases**: Track legal cases and hearings
* **Documents**: Store and manage legal documents
* **Reminders**: Task and deadline management
* **Tickets**: Support ticket system
* **Financial**: Invoicing and payment tracking
* **AI Assistant**: LLM-powered legal assistant
"""

# ==================== PAGINATION ====================

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000
DEFAULT_SKIP = 0


# ==================== FILE UPLOAD ====================

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_DOCUMENT_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.txt', '.rtf',
    '.jpg', '.jpeg', '.png', '.gif',
    '.xls', '.xlsx', '.csv'
}

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

UPLOAD_DIR = "uploads"
DOCUMENTS_DIR = f"{UPLOAD_DIR}/documents"
IMAGES_DIR = f"{UPLOAD_DIR}/images"
TEMP_DIR = f"{UPLOAD_DIR}/temp"


# ==================== DATE & TIME ====================

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

HIJRI_MONTHS_AR = [
    "محرم", "صفر", "ربيع الأول", "ربيع الآخر",
    "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان",
    "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
]


# ==================== NOTIFICATION TYPES ====================

class NotificationType(str, Enum):
    """Types of notifications"""
    REMINDER = "reminder"
    CASE_UPDATE = "case_update"
    DOCUMENT_UPLOAD = "document_upload"
    TICKET_ASSIGNED = "ticket_assigned"
    TICKET_STATUS_CHANGE = "ticket_status_change"
    PAYMENT_RECEIVED = "payment_received"
    HEARING_SCHEDULED = "hearing_scheduled"
    DEADLINE_APPROACHING = "deadline_approaching"
    SYSTEM = "system"
    OTHER = "other"


# ==================== PRIORITY LEVELS ====================

class PriorityLevel(str, Enum):
    """Priority levels for tasks, tickets, etc."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


# ==================== STATUS VALUES ====================

class ReminderStatus(str, Enum):
    """Reminder statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class TicketStatus(str, Enum):
    """Ticket statuses"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_RESPONSE = "waiting_response"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CaseStatus(str, Enum):
    """Case statuses"""
    PENDING = "pending"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    CLOSED = "closed"
    WON = "won"
    LOST = "lost"
    SETTLED = "settled"


class DocumentStatus(str, Enum):
    """Document statuses"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


# ==================== USER ROLES ====================

class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    LAWYER = "lawyer"
    STAFF = "staff"
    CLIENT = "client"


# ==================== DOCUMENT TYPES ====================

class DocumentType(str, Enum):
    """Types of legal documents"""
    CONTRACT = "contract"
    COURT_FILING = "court_filing"
    EVIDENCE = "evidence"
    CORRESPONDENCE = "correspondence"
    POWER_OF_ATTORNEY = "power_of_attorney"
    ID_DOCUMENT = "id_document"
    FINANCIAL = "financial"
    OTHER = "other"


# ==================== CASE TYPES ====================

class CaseType(str, Enum):
    """Types of legal cases"""
    CIVIL = "civil"
    CRIMINAL = "criminal"
    COMMERCIAL = "commercial"
    FAMILY = "family"
    LABOR = "labor"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


# ==================== TICKET TYPES ====================

class TicketType(str, Enum):
    """Types of support tickets"""
    SUPPORT = "support"
    REQUEST = "request"
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    FEEDBACK = "feedback"
    OTHER = "other"


# ==================== PAYMENT METHODS ====================

class PaymentMethod(str, Enum):
    """Payment methods"""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    ONLINE = "online"
    OTHER = "other"


# ==================== PAYMENT STATUS ====================

class PaymentStatus(str, Enum):
    """Payment statuses"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


# ==================== INVOICE STATUS ====================

class InvoiceStatus(str, Enum):
    """Invoice statuses"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


# ==================== ERROR MESSAGES ====================

ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "البريد الإلكتروني أو كلمة المرور غير صحيحة",
    "USER_NOT_FOUND": "المستخدم غير موجود",
    "EMAIL_EXISTS": "البريد الإلكتروني مسجل بالفعل",
    "INACTIVE_USER": "الحساب غير نشط",
    "INSUFFICIENT_PERMISSIONS": "صلاحيات غير كافية",
    "RESOURCE_NOT_FOUND": "المورد غير موجود",
    "INVALID_TOKEN": "رمز المصادقة غير صالح",
    "TOKEN_EXPIRED": "انتهت صلاحية رمز المصادقة",
    "FILE_TOO_LARGE": "الملف كبير جداً",
    "INVALID_FILE_TYPE": "نوع الملف غير مدعوم",
    "VALIDATION_ERROR": "خطأ في التحقق من البيانات",
    "DATABASE_ERROR": "خطأ في قاعدة البيانات",
    "DUPLICATE_ENTRY": "البيانات مكررة",
    "RATE_LIMIT_EXCEEDED": "تم تجاوز الحد المسموح من الطلبات",
}


# ==================== SUCCESS MESSAGES ====================

SUCCESS_MESSAGES = {
    "USER_CREATED": "تم إنشاء المستخدم بنجاح",
    "USER_UPDATED": "تم تحديث المستخدم بنجاح",
    "USER_DELETED": "تم حذف المستخدم بنجاح",
    "LOGIN_SUCCESS": "تم تسجيل الدخول بنجاح",
    "LOGOUT_SUCCESS": "تم تسجيل الخروج بنجاح",
    "PASSWORD_CHANGED": "تم تغيير كلمة المرور بنجاح",
    "EMAIL_SENT": "تم إرسال البريد الإلكتروني بنجاح",
    "FILE_UPLOADED": "تم رفع الملف بنجاح",
    "RESOURCE_CREATED": "تم إنشاء المورد بنجاح",
    "RESOURCE_UPDATED": "تم تحديث المورد بنجاح",
    "RESOURCE_DELETED": "تم حذف المورد بنجاح",
}


# ==================== REGEX PATTERNS ====================

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PHONE_REGEX = r"^(\+\d{1,3}[- ]?)?\d{10}$"
SAUDI_NATIONAL_ID_REGEX = r"^[12]\d{9}$"
SAUDI_IQAMA_REGEX = r"^2\d{9}$"


# ==================== CACHE SETTINGS ====================

CACHE_TTL = 3600  # 1 hour
CACHE_PREFIX = "legal_tech"


# ==================== SECURITY ====================

PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = False

MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 900  # 15 minutes

TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
REFRESH_TOKEN_EXPIRE_DAYS = 30


# ==================== LOGGING ====================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"


# ==================== FEATURE FLAGS ====================

FEATURES = {
    "AI_ASSISTANT": True,
    "HIJRI_CALENDAR": True,
    "EMAIL_NOTIFICATIONS": False,
    "SMS_NOTIFICATIONS": False,
    "FILE_ENCRYPTION": False,
    "TWO_FACTOR_AUTH": False,
    "AUDIT_LOG": True,
}


# ==================== BUSINESS RULES ====================

# Case deadlines (in days)
DEFAULT_CASE_DEADLINE = 30
URGENT_CASE_DEADLINE = 7

# Reminder advance notice (in days)
DEFAULT_REMINDER_ADVANCE = 3

# Document retention (in days)
DOCUMENT_RETENTION_PERIOD = 365 * 7  # 7 years

# Invoice payment terms (in days)
DEFAULT_PAYMENT_TERMS = 30
OVERDUE_GRACE_PERIOD = 7


# ==================== EXTERNAL SERVICES ====================

# AI/LLM Settings
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_MAX_TOKENS = 4000
LLM_TEMPERATURE = 0.7

# Email Settings (placeholders)
SMTP_HOST = "smtp.example.com"
SMTP_PORT = 587
EMAIL_FROM = "noreply@legaltech.com"

# SMS Settings (placeholders)
SMS_PROVIDER = "twilio"
SMS_FROM = "+1234567890"
