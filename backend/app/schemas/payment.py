"""Payment-related schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PaymentType(str, Enum):
    PREMIUM = "premium"
    CLAIM_PAYOUT = "claim_payout"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"


class PaymentCreate(BaseModel):
    """Schema for creating a payment."""
    policy_id: Optional[str] = None
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod = PaymentMethod.CARD
    description: Optional[str] = None


class PaymentIntentCreate(BaseModel):
    """Schema for creating a Stripe payment intent."""
    policy_id: str
    amount: float = Field(..., gt=0)
    currency: str = "usd"


class PaymentIntentResponse(BaseModel):
    """Schema for Stripe payment intent response."""
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str


class PaymentResponse(BaseModel):
    """Schema for payment response."""
    id: str
    payment_type: str
    payment_method: Optional[str] = None
    amount: float
    currency: str
    status: str
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    policy_id: Optional[str] = None
    claim_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentSummary(BaseModel):
    """Schema for payment summary."""
    total_paid: float
    total_pending: float
    total_refunded: float
    last_payment_date: Optional[datetime] = None
    next_due_date: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    """Schema for invoice response."""
    id: str
    invoice_number: str
    policy_id: str
    amount: float
    currency: str
    status: str
    due_date: datetime
    paid_date: Optional[datetime] = None
    pdf_url: Optional[str] = None
    created_at: datetime


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""
    policy_id: str
    payment_method_id: str
    billing_cycle: str = "monthly"  # monthly, quarterly, annually


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""
    id: str
    policy_id: str
    stripe_subscription_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    billing_cycle: str
    amount: float
    currency: str
