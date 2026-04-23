"""Admin API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import User
from app.models.policy import Policy, PolicyStatus
from app.models.claim import Claim, ClaimStatus
from app.models.payment import Payment, PaymentStatus
from app.models.audit_log import AuditLog
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus
from app.schemas.claim import ClaimReview
from datetime import datetime, timedelta

router = APIRouter()

async def verify_admin(user_id: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/dashboard")
async def get_admin_dashboard(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await verify_admin(user_id, db)
    
    total_users = (await db.execute(select(func.count(User.id)).where(User.is_deleted == False))).scalar() or 0
    active_policies = (await db.execute(select(func.count(Policy.id)).where(Policy.status == PolicyStatus.ACTIVE))).scalar() or 0
    pending_claims = (await db.execute(select(func.count(Claim.id)).where(Claim.status.in_([ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW])))).scalar() or 0
    total_revenue = float((await db.execute(select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.COMPLETED))).scalar() or 0)
    
    review_claims = (await db.execute(select(Claim).where(Claim.status == ClaimStatus.SUBMITTED).order_by(Claim.created_at.asc()).limit(10))).scalars().all()
    
    return {
        "users": {"total": total_users},
        "policies": {"active": active_policies},
        "claims": {"pending_review": pending_claims},
        "revenue": {"total": total_revenue},
        "claims_for_review": [c.to_dict() for c in review_claims]
    }

@router.get("/users")
async def list_users(page: int = 1, per_page: int = 20, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await verify_admin(user_id, db)
    total = (await db.execute(select(func.count(User.id)).where(User.is_deleted == False))).scalar() or 0
    users = (await db.execute(select(User).where(User.is_deleted == False).order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page))).scalars().all()
    return {"data": [u.to_dict() for u in users], "meta": {"page": page, "per_page": per_page, "total": total}}

@router.get("/claims")
async def list_claims(page: int = 1, per_page: int = 20, status_filter: str = None, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await verify_admin(user_id, db)
    query = select(Claim).where(Claim.is_deleted == False)
    if status_filter: query = query.where(Claim.status == ClaimStatus(status_filter))
    total = (await db.execute(select(func.count(Claim.id)).where(Claim.is_deleted == False))).scalar() or 0
    claims = (await db.execute(query.order_by(Claim.created_at.desc()).offset((page - 1) * per_page).limit(per_page))).scalars().all()
    return {"data": [c.to_dict() for c in claims], "meta": {"page": page, "per_page": per_page, "total": total}}

@router.put("/claims/{claim_id}/review")
async def review_claim(claim_id: str, review_data: ClaimReview, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    admin = await verify_admin(user_id, db)
    claim = (await db.execute(select(Claim).where(Claim.id == claim_id))).scalar_one_or_none()
    if not claim: raise HTTPException(status_code=404, detail="Claim not found")
    
    claim.status = review_data.status
    if review_data.approved_amount: claim.approved_amount = review_data.approved_amount
    if review_data.reviewer_notes: claim.reviewer_notes = review_data.reviewer_notes
    claim.reviewed_by = user_id
    claim.reviewed_at = datetime.utcnow()
    
    notification = Notification(user_id=claim.user_id, notification_type=NotificationType.CLAIM_APPROVED if review_data.status == ClaimStatus.APPROVED else NotificationType.CLAIM_REJECTED, channel=NotificationChannel.IN_APP, subject=f"Claim {review_data.status.value}", content=f"Your claim {claim.claim_number} has been {review_data.status.value}.", status=NotificationStatus.SENT, sent_at=datetime.utcnow())
    db.add(notification)
    
    audit = AuditLog(user_id=user_id, action="claim_reviewed", entity_type="claim", entity_id=claim_id)
    db.add(audit)
    await db.commit()
    return claim.to_dict()

@router.post("/users/{target_user_id}/deactivate")
async def deactivate_user(target_user_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await verify_admin(user_id, db)
    user = (await db.execute(select(User).where(User.id == target_user_id))).scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.commit()
    return {"success": True, "message": "User deactivated"}

@router.post("/users/{target_user_id}/activate")
async def activate_user(target_user_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await verify_admin(user_id, db)
    user = (await db.execute(select(User).where(User.id == target_user_id))).scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    await db.commit()
    return {"success": True, "message": "User activated"}
