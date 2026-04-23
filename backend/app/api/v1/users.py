"""User API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id, hash_password, verify_password
from app.models.user import User
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.schemas.user import UserResponse, UserUpdate, ChangePassword
from app.schemas.common import MessageResponse, PaginatedResponse
from typing import List
from datetime import datetime

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        address=user.address,
        date_of_birth=user.date_of_birth,
        kyc_status=user.kyc_status.value,
        gdpr_consent=user.gdpr_consent,
        mfa_enabled=user.mfa_enabled,
        is_admin=user.is_admin,
        created_at=user.created_at
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Store old values for audit
    old_values = {
        "full_name": user.full_name,
        "phone": user.phone,
        "address": user.address,
        "date_of_birth": str(user.date_of_birth) if user.date_of_birth else None
    }
    
    # Update fields
    if update_data.full_name is not None:
        user.full_name = update_data.full_name
    if update_data.phone is not None:
        user.phone = update_data.phone
    if update_data.address is not None:
        user.address = update_data.address
    if update_data.date_of_birth is not None:
        user.date_of_birth = update_data.date_of_birth
    
    user.updated_at = datetime.utcnow()
    
    # Audit log
    new_values = {
        "full_name": user.full_name,
        "phone": user.phone,
        "address": user.address,
        "date_of_birth": str(user.date_of_birth) if user.date_of_birth else None
    }
    
    audit = AuditLog(
        user_id=user_id,
        action="user_profile_updated",
        entity_type="user",
        entity_id=user_id,
        old_values=old_values,
        new_values=new_values
    )
    db.add(audit)
    
    await db.commit()
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        address=user.address,
        date_of_birth=user.date_of_birth,
        kyc_status=user.kyc_status.value,
        gdpr_consent=user.gdpr_consent,
        mfa_enabled=user.mfa_enabled,
        is_admin=user.is_admin,
        created_at=user.created_at
    )


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Verify new passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Update password
    user.password_hash = hash_password(password_data.new_password)
    user.updated_at = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="password_changed",
        entity_type="user",
        entity_id=user_id
    )
    db.add(audit)
    
    await db.commit()
    
    return MessageResponse(message="Password changed successfully")


@router.get("/me/notifications", response_model=List[dict])
async def get_notifications(
    page: int = 1,
    per_page: int = 20,
    unread_only: bool = False,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get user notifications."""
    query = select(Notification).where(Notification.user_id == user_id)
    
    if unread_only:
        query = query.where(Notification.is_read == False)
    
    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return [n.to_dict() for n in notifications]


@router.put("/me/notifications/{notification_id}/read", response_model=MessageResponse)
async def mark_notification_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    
    await db.commit()
    
    return MessageResponse(message="Notification marked as read")


@router.get("/me/dashboard", response_model=dict)
async def get_dashboard_data(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard summary data."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get counts
    from app.models.policy import Policy, PolicyStatus
    from app.models.claim import Claim
    from app.models.payment import Payment
    
    # Active policies
    policies_result = await db.execute(
        select(Policy).where(
            Policy.user_id == user_id,
            Policy.status == PolicyStatus.ACTIVE,
            Policy.is_deleted == False
        )
    )
    active_policies = policies_result.scalars().all()
    
    # Pending claims
    from app.models.claim import ClaimStatus
    claims_result = await db.execute(
        select(Claim).where(
            Claim.user_id == user_id,
            Claim.status.in_([ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW]),
            Claim.is_deleted == False
        )
    )
    pending_claims = claims_result.scalars().all()
    
    # Recent payments
    payments_result = await db.execute(
        select(Payment).where(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .limit(5)
    )
    recent_payments = payments_result.scalars().all()
    
    # Unread notifications
    notif_result = await db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    unread_notifications = len(notif_result.scalars().all())
    
    # Total coverage
    total_coverage = sum(float(p.coverage_amount) for p in active_policies)
    
    return {
        "user": {
            "full_name": user.full_name,
            "email": user.email,
            "kyc_status": user.kyc_status.value
        },
        "summary": {
            "active_policies": len(active_policies),
            "pending_claims": len(pending_claims),
            "total_coverage": total_coverage,
            "unread_notifications": unread_notifications
        },
        "recent_policies": [p.to_dict() for p in active_policies[:3]],
        "recent_payments": [p.to_dict() for p in recent_payments]
    }
