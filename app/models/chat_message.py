"""
Chat Message Model
Stores conversation history with AI assistant
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ChatMessage(BaseModel):
    """Chat message between user and AI assistant"""
    
    __tablename__ = "chat_messages"
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    content_ar = Column(Text)  # Arabic translation
    
    # Conversation context
    session_id = Column(String(100), index=True)  # Group messages by session
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    
    # User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="chat_messages")
    
    # Metadata
    model_used = Column(String(100))  # Which AI model was used
    tokens_used = Column(Integer)  # Token count for billing
    metadata = Column(JSON)  # Additional data (tools used, citations, etc.)
    
    # Feedback
    is_helpful = Column(Boolean, default=None)  # User feedback
    feedback_comment = Column(Text)  # Detailed feedback
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, user_id={self.user_id})>"


class Conversation(BaseModel):
    """Conversation/thread containing multiple messages"""
    
    __tablename__ = "conversations"
    
    title = Column(String(200))
    title_ar = Column(String(200))
    
    # User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="conversations")
    
    # Messages
    messages = relationship("ChatMessage", back_populates="conversation")
    
    # Metadata
    is_archived = Column(Boolean, default=False)
    tags = Column(JSON)  # Categorize conversations
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"
