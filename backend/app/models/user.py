"""User database model."""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class User(Base):
    """User model for storing user information."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(JSON, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    kyc_status = Column(SQLEnum(KYCStatus), default=KYCStatus.PENDING)
    gdpr_consent = Column(Boolean, default=False)
    gdpr_consent_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    policies = relationship("Policy", back_populates="user", lazy="selectin")
    claims = relationship("Claim", back_populates="user", lazy="selectin")
    payments = relationship("Payment", back_populates="user", lazy="selectin")
    sessions = relationship("Session", back_populates="user", lazy="selectin")
    audit_logs = relationship("AuditLog", back_populates="user", lazy="selectin")
    consents = relationship("GDPRConsent", back_populates="user", lazy="selectin")
    notifications = relationship("Notification", back_populates="user", lazy="selectin")
    documents = relationship("Document", back_populates="user", lazy="selectin")
    chat_history = relationship("ChatHistory", back_populates="user", lazy="selectin")
    quotes = relationship("Quote", back_populates="user", lazy="selectin")
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "address": self.address,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "kyc_status": self.kyc_status.value,
            "gdpr_consent": self.gdpr_consent,
            "mfa_enabled": self.mfa_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
