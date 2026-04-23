"""Chat history database model."""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class ChatRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatHistory(Base):
    """Chat history model for storing AI conversations."""
    
    __tablename__ = "chat_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(SQLEnum(ChatRole), nullable=False)
    message = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    entities = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
    
    def to_dict(self):
        """Convert chat history to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role.value,
            "message": self.message,
            "intent": self.intent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
