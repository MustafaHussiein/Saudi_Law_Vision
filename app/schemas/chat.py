"""
Chat and AI Assistant schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.base import TimestampSchema


class ChatMessageBase(BaseModel):
    """Base chat message schema"""
    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field(..., pattern="^(user|assistant)$")


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating chat message"""
    session_id: Optional[str] = None
    conversation_id: Optional[int] = None


class ChatMessageResponse(ChatMessageBase, TimestampSchema):
    """Schema for chat message response"""
    user_id: int
    session_id: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    is_helpful: Optional[bool] = None


class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Schema for creating conversation"""
    pass


class ConversationResponse(ConversationBase, TimestampSchema):
    """Schema for conversation response"""
    user_id: int
    is_archived: bool
    message_count: int = 0
