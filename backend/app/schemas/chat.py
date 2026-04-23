"""Chat-related schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Schema for a chat message."""
    role: ChatRole
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: str
    session_id: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    requires_action: bool = False
    action_type: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class ChatHistory(BaseModel):
    """Schema for chat history."""
    id: str
    session_id: str
    role: str
    message: str
    intent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSession(BaseModel):
    """Schema for chat session."""
    session_id: str
    started_at: datetime
    last_message_at: datetime
    message_count: int
    current_intent: Optional[str] = None


class ChatFeedback(BaseModel):
    """Schema for chat feedback."""
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None


class ClaimChatContext(BaseModel):
    """Schema for claim filing chat context."""
    step: str
    policy_id: Optional[str] = None
    claim_type: Optional[str] = None
    description: Optional[str] = None
    incident_date: Optional[datetime] = None
    claimed_amount: Optional[float] = None
    collected_info: Dict[str, Any] = {}
