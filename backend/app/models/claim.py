"""Claim database model."""
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum, ForeignKey, Numeric, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class ClaimType(str, enum.Enum):
    PROPERTY_DAMAGE = "property_damage"
    THEFT = "theft"
    WATER_DAMAGE = "water_damage"
    FIRE_DAMAGE = "fire_damage"
    LIABILITY = "liability"
    MEDICAL = "medical"
    ACCIDENT = "accident"
    NATURAL_DISASTER = "natural_disaster"
    OTHER = "other"


class ClaimStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    CLOSED = "closed"


class Claim(Base):
    """Claim model for storing insurance claims."""
    
    __tablename__ = "claims"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id = Column(String(36), ForeignKey("policies.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    claim_number = Column(String(50), unique=True, nullable=False)
    claim_type = Column(SQLEnum(ClaimType), nullable=False)
    description = Column(Text, nullable=False)
    incident_date = Column(DateTime, nullable=False)
    incident_location = Column(JSON, nullable=True)
    claimed_amount = Column(Numeric(12, 2), nullable=False)
    approved_amount = Column(Numeric(12, 2), nullable=True)
    status = Column(SQLEnum(ClaimStatus), default=ClaimStatus.DRAFT)
    ai_assessment = Column(JSON, nullable=True)
    fraud_score = Column(Numeric(5, 4), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(36), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    policy = relationship("Policy", back_populates="claims")
    user = relationship("User", back_populates="claims")
    documents = relationship("Document", back_populates="claim", lazy="selectin")
    payments = relationship("Payment", back_populates="claim", lazy="selectin")
    
    def to_dict(self):
        """Convert claim to dictionary."""
        return {
            "id": self.id,
            "claim_number": self.claim_number,
            "policy_id": self.policy_id,
            "claim_type": self.claim_type.value,
            "description": self.description,
            "incident_date": self.incident_date.isoformat() if self.incident_date else None,
            "incident_location": self.incident_location,
            "claimed_amount": float(self.claimed_amount),
            "approved_amount": float(self.approved_amount) if self.approved_amount else None,
            "status": self.status.value,
            "ai_assessment": self.ai_assessment,
            "fraud_score": float(self.fraud_score) if self.fraud_score else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
