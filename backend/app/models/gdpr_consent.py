"""GDPR Consent database model."""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class ConsentType(str, enum.Enum):
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    MARKETING_EMAIL = "marketing_email"
    MARKETING_SMS = "marketing_sms"
    DATA_PROCESSING = "data_processing"
    THIRD_PARTY_SHARING = "third_party_sharing"
    ANALYTICS = "analytics"


class GDPRConsent(Base):
    """GDPR Consent model for tracking user consents."""
    
    __tablename__ = "gdpr_consents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    consent_type = Column(SQLEnum(ConsentType), nullable=False)
    granted = Column(Boolean, default=False)
    version = Column(String(20), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    granted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="consents")
    
    def to_dict(self):
        """Convert consent to dictionary."""
        return {
            "id": self.id,
            "consent_type": self.consent_type.value,
            "granted": self.granted,
            "version": self.version,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }
