"""Quote database model."""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Numeric, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class QuoteStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    READY = "ready"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REJECTED = "rejected"


class Quote(Base):
    """Quote model for storing insurance quotes."""
    
    __tablename__ = "quotes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    quote_number = Column(String(50), unique=True, nullable=False)
    policy_type = Column(String(50), nullable=False)
    coverage_amount = Column(Numeric(12, 2), nullable=False)
    premium_amount = Column(Numeric(10, 2), nullable=False)
    deductible = Column(Numeric(10, 2), default=0)
    details = Column(JSON, nullable=True)
    risk_assessment = Column(JSON, nullable=True)
    status = Column(SQLEnum(QuoteStatus), default=QuoteStatus.DRAFT)
    valid_until = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="quotes")
    
    def to_dict(self):
        """Convert quote to dictionary."""
        return {
            "id": self.id,
            "quote_number": self.quote_number,
            "policy_type": self.policy_type,
            "coverage_amount": float(self.coverage_amount),
            "premium_amount": float(self.premium_amount),
            "deductible": float(self.deductible) if self.deductible else 0,
            "details": self.details,
            "status": self.status.value,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
