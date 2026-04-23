"""Payments API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.config import settings
from app.models.payment import Payment, PaymentType, PaymentStatus, PaymentMethod
from app.models.policy import Policy
from app.models.audit_log import AuditLog
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentIntentCreate, 
    PaymentIntentResponse, PaymentSummary
)
from app.schemas.common import MessageResponse
from typing import List
from datetime import datetime

router = APIRouter()


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a Stripe payment intent."""
    # Verify policy
    result = await db.execute(
        select(Policy).where(
            Policy.id == payment_data.policy_id,
            Policy.user_id == user_id
        )
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # In production, this would create a real Stripe PaymentIntent
    # For now, return mock data
    mock_intent = {
        "client_secret": f"pi_{datetime.utcnow().timestamp()}_secret_mock",
        "payment_intent_id": f"pi_{datetime.utcnow().timestamp()}_mock",
        "amount": payment_data.amount,
        "currency": payment_data.currency
    }
    
    return PaymentIntentResponse(**mock_intent)


@router.post("/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_intent_id: str,
    policy_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Confirm a payment after Stripe processing."""
    # Verify policy
    result = await db.execute(
        select(Policy).where(
            Policy.id == policy_id,
            Policy.user_id == user_id
        )
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Create payment record
    payment = Payment(
        user_id=user_id,
        policy_id=policy_id,
        payment_type=PaymentType.PREMIUM,
        payment_method=PaymentMethod.CARD,
        amount=policy.premium_amount,
        currency="USD",
        stripe_payment_id=payment_intent_id,
        status=PaymentStatus.COMPLETED,
        description=f"Premium payment for policy {policy.policy_number}",
        payment_date=datetime.utcnow()
    )
    
    db.add(payment)
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="payment_completed",
        entity_type="payment",
        entity_id=payment.id,
        new_values=payment.to_dict()
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(payment)
    
    return PaymentResponse(
        id=payment.id,
        payment_type=payment.payment_type.value,
        payment_method=payment.payment_method.value,
        amount=float(payment.amount),
        currency=payment.currency,
        status=payment.status.value,
        description=payment.description,
        receipt_url=payment.receipt_url,
        policy_id=payment.policy_id,
        payment_date=payment.payment_date,
        created_at=payment.created_at
    )


@router.get("", response_model=List[PaymentResponse])
async def get_payments(
    page: int = 1,
    per_page: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get payment history."""
    query = select(Payment).where(
        Payment.user_id == user_id,
        Payment.is_deleted == False
    ).order_by(Payment.created_at.desc())
    
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    payments = result.scalars().all()
    
    return [
        PaymentResponse(
            id=p.id,
            payment_type=p.payment_type.value,
            payment_method=p.payment_method.value if p.payment_method else None,
            amount=float(p.amount),
            currency=p.currency,
            status=p.status.value,
            description=p.description,
            receipt_url=p.receipt_url,
            policy_id=p.policy_id,
            claim_id=p.claim_id,
            payment_date=p.payment_date,
            created_at=p.created_at
        )
        for p in payments
    ]


@router.get("/summary", response_model=PaymentSummary)
async def get_payment_summary(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get payment summary for user."""
    # Total paid
    paid_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.user_id == user_id,
            Payment.status == PaymentStatus.COMPLETED,
            Payment.payment_type == PaymentType.PREMIUM
        )
    )
    total_paid = paid_result.scalar() or 0
    
    # Total pending
    pending_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.user_id == user_id,
            Payment.status == PaymentStatus.PENDING
        )
    )
    total_pending = pending_result.scalar() or 0
    
    # Total refunded
    refunded_result = await db.execute(
        select(func.sum(Payment.amount)).where(
            Payment.user_id == user_id,
            Payment.status == PaymentStatus.REFUNDED
        )
    )
    total_refunded = refunded_result.scalar() or 0
    
    # Last payment date
    last_payment_result = await db.execute(
        select(Payment.payment_date).where(
            Payment.user_id == user_id,
            Payment.status == PaymentStatus.COMPLETED
        ).order_by(Payment.payment_date.desc()).limit(1)
    )
    last_payment_date = last_payment_result.scalar()
    
    return PaymentSummary(
        total_paid=float(total_paid),
        total_pending=float(total_pending),
        total_refunded=float(total_refunded),
        last_payment_date=last_payment_date
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific payment."""
    result = await db.execute(
        select(Payment).where(
            Payment.id == payment_id,
            Payment.user_id == user_id,
            Payment.is_deleted == False
        )
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentResponse(
        id=payment.id,
        payment_type=payment.payment_type.value,
        payment_method=payment.payment_method.value if payment.payment_method else None,
        amount=float(payment.amount),
        currency=payment.currency,
        status=payment.status.value,
        description=payment.description,
        receipt_url=payment.receipt_url,
        policy_id=payment.policy_id,
        claim_id=payment.claim_id,
        payment_date=payment.payment_date,
        created_at=payment.created_at
    )


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Request a refund for a payment."""
    result = await db.execute(
        select(Payment).where(
            Payment.id == payment_id,
            Payment.user_id == user_id,
            Payment.is_deleted == False
        )
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund completed payments"
        )
    
    # In production, process refund through Stripe
    payment.status = PaymentStatus.REFUNDED
    payment.updated_at = datetime.utcnow()
    
    # Create refund record
    refund = Payment(
        user_id=user_id,
        policy_id=payment.policy_id,
        payment_type=PaymentType.REFUND,
        payment_method=payment.payment_method,
        amount=-payment.amount,  # Negative for refund
        currency=payment.currency,
        status=PaymentStatus.COMPLETED,
        description=f"Refund for payment {payment.id}",
        payment_date=datetime.utcnow()
    )
    db.add(refund)
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="payment_refunded",
        entity_type="payment",
        entity_id=payment_id
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(payment)
    
    return PaymentResponse(
        id=payment.id,
        payment_type=payment.payment_type.value,
        payment_method=payment.payment_method.value if payment.payment_method else None,
        amount=float(payment.amount),
        currency=payment.currency,
        status=payment.status.value,
        description=payment.description,
        receipt_url=payment.receipt_url,
        policy_id=payment.policy_id,
        payment_date=payment.payment_date,
        created_at=payment.created_at
    )
