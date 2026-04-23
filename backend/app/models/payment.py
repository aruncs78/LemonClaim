"""Payment database model."""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class PaymentType(str, enum.Enum):
    PREMIUM = "premium"
    CLAIM_PAYOUT = "claim_payout"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"


class Payment(Base):
    """Payment model for storing transactions."""
    
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    policy_id = Column(String(36), ForeignKey("policies.id"), nullable=True, index=True)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=True, index=True)
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    stripe_payment_id = Column(String(100), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    description = Column(String(500), nullable=True)
    receipt_url = Column(String(500), nullable=True)
    failure_reason = Column(String(500), nullable=True)
    is_deleted = Column(Boolean, default=False)
    payment_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    policy = relationship("Policy", back_populates="payments")
    claim = relationship("Claim", back_populates="payments")
    
    def to_dict(self):
        """Convert payment to dictionary."""
        return {
            "id": self.id,
            "payment_type": self.payment_type.value,
            "payment_method": self.payment_method.value if self.payment_method else None,
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status.value,
            "description": self.description,
            "receipt_url": self.receipt_url,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
