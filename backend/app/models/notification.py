"""Notification database model."""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class NotificationType(str, enum.Enum):
    WELCOME = "welcome"
    POLICY_CREATED = "policy_created"
    POLICY_RENEWED = "policy_renewed"
    POLICY_EXPIRING = "policy_expiring"
    CLAIM_SUBMITTED = "claim_submitted"
    CLAIM_APPROVED = "claim_approved"
    CLAIM_REJECTED = "claim_rejected"
    CLAIM_PAID = "claim_paid"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    PASSWORD_RESET = "password_reset"
    SECURITY_ALERT = "security_alert"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    """Notification model for storing user notifications."""
    
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    external_id = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            "id": self.id,
            "notification_type": self.notification_type.value,
            "channel": self.channel.value,
            "subject": self.subject,
            "content": self.content,
            "status": self.status.value,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
