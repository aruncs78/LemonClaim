"""Policy API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.policy import Policy, PolicyType, PolicyStatus
from app.models.quote import Quote, QuoteStatus
from app.models.audit_log import AuditLog
from app.schemas.policy import (
    PolicyCreate, PolicyUpdate, PolicyResponse, PolicySummary,
    QuoteRequest, QuoteResponse
)
from app.schemas.common import MessageResponse, PaginatedResponse
from typing import List
from datetime import datetime, timedelta
import uuid
import random

router = APIRouter()


def generate_policy_number() -> str:
    """Generate a unique policy number."""
    prefix = "LC"
    timestamp = datetime.utcnow().strftime("%y%m")
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{prefix}-{timestamp}-{random_part}"


def generate_quote_number() -> str:
    """Generate a unique quote number."""
    prefix = "QT"
    timestamp = datetime.utcnow().strftime("%y%m%d")
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return f"{prefix}-{timestamp}-{random_part}"


def calculate_premium(quote_request: QuoteRequest) -> float:
    """Calculate premium based on coverage and risk factors."""
    base_rate = 0.0
    
    # Base rates by policy type
    base_rates = {
        PolicyType.HOME: 0.003,
        PolicyType.RENTERS: 0.012,
        PolicyType.AUTO: 0.05,
        PolicyType.LIFE: 0.008,
        PolicyType.PET: 0.15,
        PolicyType.TRAVEL: 0.04
    }
    
    base_rate = base_rates.get(quote_request.policy_type, 0.01)
    
    # Calculate base premium
    premium = quote_request.coverage_amount * base_rate
    
    # Apply risk adjustments
    risk_multiplier = 1.0
    
    # Home/Renters adjustments
    if quote_request.policy_type in [PolicyType.HOME, PolicyType.RENTERS]:
        if quote_request.year_built and quote_request.year_built < 1980:
            risk_multiplier += 0.15
        if quote_request.security_system:
            risk_multiplier -= 0.1
    
    # Life adjustments
    if quote_request.policy_type == PolicyType.LIFE:
        if quote_request.smoker:
            risk_multiplier += 0.5
    
    # Apply deductible discount
    if quote_request.deductible >= 1000:
        risk_multiplier -= 0.1
    elif quote_request.deductible >= 500:
        risk_multiplier -= 0.05
    
    premium *= max(risk_multiplier, 0.5)  # Minimum 50% of base
    
    # Annual premium, minimum $50
    return max(round(premium, 2), 50.0)


@router.post("/quote", response_model=QuoteResponse)
async def get_quote(
    quote_request: QuoteRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get an insurance quote."""
    premium = calculate_premium(quote_request)
    
    # Create quote record
    quote = Quote(
        user_id=user_id,
        quote_number=generate_quote_number(),
        policy_type=quote_request.policy_type.value,
        coverage_amount=quote_request.coverage_amount,
        premium_amount=premium,
        deductible=quote_request.deductible,
        details={
            "property_type": quote_request.property_type,
            "property_value": quote_request.property_value,
            "square_footage": quote_request.square_footage,
            "year_built": quote_request.year_built,
            "security_system": quote_request.security_system,
            "vehicle_make": quote_request.vehicle_make,
            "vehicle_model": quote_request.vehicle_model,
            "vehicle_year": quote_request.vehicle_year,
            "pet_type": quote_request.pet_type,
            "pet_breed": quote_request.pet_breed,
            "pet_age": quote_request.pet_age
        },
        risk_assessment={
            "risk_score": random.uniform(0.1, 0.5),
            "factors": []
        },
        status=QuoteStatus.READY,
        valid_until=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(quote)
    await db.commit()
    await db.refresh(quote)
    
    return QuoteResponse(
        id=quote.id,
        quote_number=quote.quote_number,
        policy_type=quote.policy_type,
        coverage_amount=float(quote.coverage_amount),
        premium_amount=float(quote.premium_amount),
        deductible=float(quote.deductible),
        monthly_premium=round(float(quote.premium_amount) / 12, 2),
        details=quote.details,
        risk_assessment=quote.risk_assessment,
        valid_until=quote.valid_until,
        created_at=quote.created_at
    )


@router.get("/quotes", response_model=List[QuoteResponse])
async def get_user_quotes(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all quotes for the current user."""
    result = await db.execute(
        select(Quote).where(
            Quote.user_id == user_id,
            Quote.is_deleted == False
        ).order_by(Quote.created_at.desc())
    )
    quotes = result.scalars().all()
    
    return [
        QuoteResponse(
            id=q.id,
            quote_number=q.quote_number,
            policy_type=q.policy_type,
            coverage_amount=float(q.coverage_amount),
            premium_amount=float(q.premium_amount),
            deductible=float(q.deductible),
            monthly_premium=round(float(q.premium_amount) / 12, 2),
            details=q.details,
            risk_assessment=q.risk_assessment,
            valid_until=q.valid_until,
            created_at=q.created_at
        )
        for q in quotes
    ]


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_data: PolicyCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new policy from a quote."""
    # Get quote
    result = await db.execute(
        select(Quote).where(
            Quote.id == policy_data.quote_id,
            Quote.user_id == user_id,
            Quote.status == QuoteStatus.READY
        )
    )
    quote = result.scalar_one_or_none()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found or expired"
        )
    
    if quote.valid_until < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quote has expired"
        )
    
    # Create policy
    start_date = policy_data.start_date or datetime.utcnow()
    
    policy = Policy(
        user_id=user_id,
        policy_number=generate_policy_number(),
        policy_type=PolicyType(quote.policy_type),
        coverage_amount=quote.coverage_amount,
        premium_amount=quote.premium_amount,
        deductible=quote.deductible,
        start_date=start_date,
        end_date=start_date + timedelta(days=365),
        status=PolicyStatus.ACTIVE,
        property_details=quote.details
    )
    
    db.add(policy)
    
    # Update quote status
    quote.status = QuoteStatus.ACCEPTED
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="policy_created",
        entity_type="policy",
        entity_id=policy.id,
        new_values=policy.to_dict()
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(policy)
    
    return PolicyResponse(
        id=policy.id,
        policy_number=policy.policy_number,
        policy_type=policy.policy_type.value,
        coverage_amount=float(policy.coverage_amount),
        premium_amount=float(policy.premium_amount),
        deductible=float(policy.deductible),
        start_date=policy.start_date,
        end_date=policy.end_date,
        status=policy.status.value,
        property_details=policy.property_details,
        claims_count=0,
        created_at=policy.created_at
    )


@router.get("", response_model=List[PolicySummary])
async def get_policies(
    status_filter: str = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all policies for the current user."""
    query = select(Policy).where(
        Policy.user_id == user_id,
        Policy.is_deleted == False
    )
    
    if status_filter:
        query = query.where(Policy.status == PolicyStatus(status_filter))
    
    query = query.order_by(Policy.created_at.desc())
    
    result = await db.execute(query)
    policies = result.scalars().all()
    
    return [
        PolicySummary(
            id=p.id,
            policy_number=p.policy_number,
            policy_type=p.policy_type.value,
            coverage_amount=float(p.coverage_amount),
            premium_amount=float(p.premium_amount),
            status=p.status.value,
            end_date=p.end_date
        )
        for p in policies
    ]


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific policy."""
    result = await db.execute(
        select(Policy).where(
            Policy.id == policy_id,
            Policy.user_id == user_id,
            Policy.is_deleted == False
        )
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Get claims count
    from app.models.claim import Claim
    claims_result = await db.execute(
        select(func.count(Claim.id)).where(Claim.policy_id == policy_id)
    )
    claims_count = claims_result.scalar() or 0
    
    return PolicyResponse(
        id=policy.id,
        policy_number=policy.policy_number,
        policy_type=policy.policy_type.value,
        coverage_amount=float(policy.coverage_amount),
        premium_amount=float(policy.premium_amount),
        deductible=float(policy.deductible),
        start_date=policy.start_date,
        end_date=policy.end_date,
        status=policy.status.value,
        property_details=policy.property_details,
        beneficiaries=policy.beneficiaries,
        claims_count=claims_count,
        created_at=policy.created_at
    )


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    update_data: PolicyUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update a policy."""
    result = await db.execute(
        select(Policy).where(
            Policy.id == policy_id,
            Policy.user_id == user_id,
            Policy.is_deleted == False
        )
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    if policy.status != PolicyStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update active policies"
        )
    
    # Update fields
    old_values = policy.to_dict()
    
    if update_data.coverage_amount is not None:
        policy.coverage_amount = update_data.coverage_amount
    if update_data.deductible is not None:
        policy.deductible = update_data.deductible
    if update_data.property_details is not None:
        policy.property_details = update_data.property_details
    if update_data.beneficiaries is not None:
        policy.beneficiaries = update_data.beneficiaries
    
    policy.updated_at = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="policy_updated",
        entity_type="policy",
        entity_id=policy_id,
        old_values=old_values,
        new_values=policy.to_dict()
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(policy)
    
    return PolicyResponse(
        id=policy.id,
        policy_number=policy.policy_number,
        policy_type=policy.policy_type.value,
        coverage_amount=float(policy.coverage_amount),
        premium_amount=float(policy.premium_amount),
        deductible=float(policy.deductible),
        start_date=policy.start_date,
        end_date=policy.end_date,
        status=policy.status.value,
        property_details=policy.property_details,
        beneficiaries=policy.beneficiaries,
        claims_count=0,
        created_at=policy.created_at
    )


@router.delete("/{policy_id}", response_model=MessageResponse)
async def cancel_policy(
    policy_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a policy."""
    result = await db.execute(
        select(Policy).where(
            Policy.id == policy_id,
            Policy.user_id == user_id,
            Policy.is_deleted == False
        )
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    if policy.status == PolicyStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Policy is already cancelled"
        )
    
    policy.status = PolicyStatus.CANCELLED
    policy.updated_at = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="policy_cancelled",
        entity_type="policy",
        entity_id=policy_id
    )
    db.add(audit)
    
    await db.commit()
    
    return MessageResponse(message="Policy cancelled successfully")
