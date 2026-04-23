"""Policy database model."""
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class PolicyType(str, enum.Enum):
    HOME = "home"
    RENTERS = "renters"
    AUTO = "auto"
    LIFE = "life"
    PET = "pet"
    TRAVEL = "travel"


class PolicyStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class Policy(Base):
    """Policy model for storing insurance policies."""
    
    __tablename__ = "policies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    policy_number = Column(String(50), unique=True, nullable=False)
    policy_type = Column(SQLEnum(PolicyType), nullable=False)
    coverage_amount = Column(Numeric(12, 2), nullable=False)
    premium_amount = Column(Numeric(10, 2), nullable=False)
    deductible = Column(Numeric(10, 2), default=0)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(SQLEnum(PolicyStatus), default=PolicyStatus.PENDING)
    property_details = Column(JSON, nullable=True)
    beneficiaries = Column(JSON, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="policies")
    claims = relationship("Claim", back_populates="policy", lazy="selectin")
    payments = relationship("Payment", back_populates="policy", lazy="selectin")
    
    def to_dict(self):
        """Convert policy to dictionary."""
        return {
            "id": self.id,
            "policy_number": self.policy_number,
            "policy_type": self.policy_type.value,
            "coverage_amount": float(self.coverage_amount),
            "premium_amount": float(self.premium_amount),
            "deductible": float(self.deductible) if self.deductible else 0,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status.value,
            "property_details": self.property_details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Fix import issue
from sqlalchemy import Boolean
