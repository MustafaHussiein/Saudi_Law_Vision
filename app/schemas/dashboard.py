"""
Dashboard Pydantic Schemas
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Dashboard statistics schema"""
    # Reminders
    total_reminders: int = 0
    pending_reminders: int = 0
    in_progress_reminders: int = 0
    completed_reminders: int = 0
    overdue_reminders: int = 0
    
    # Tickets
    total_tickets: int = 0
    open_tickets: int = 0
    in_progress_tickets: int = 0
    resolved_tickets: int = 0
    
    # Cases
    total_cases: int = 0
    active_cases: int = 0
    pending_cases: int = 0
    closed_cases: int = 0
    
    # Clients
    total_clients: int = 0
    active_clients: int = 0
    
    # Notifications
    unread_notifications: int = 0
    
    # Financial
    total_revenue: float = 0
    pending_invoices: int = 0
    overdue_invoices: int = 0


class QuickStats(BaseModel):
    """Quick stats for dashboard cards"""
    pending: int = 0
    in_progress: int = 0
    assigned: int = 0
    waiting: int = 0


class ActivityItem(BaseModel):
    """Recent activity item"""
    id: int
    type: str  # reminder, ticket, case, document
    title: str
    description: Optional[str] = None
    timestamp: str
    user: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class DashboardResponse(BaseModel):
    """Complete dashboard response"""
    stats: DashboardStats
    quick_stats: QuickStats
    recent_activity: list[ActivityItem] = []
    charts_data: Optional[Dict[str, Any]] = None
