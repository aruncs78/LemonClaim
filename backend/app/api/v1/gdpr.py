"""GDPR compliance API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import User
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.payment import Payment
from app.models.gdpr_consent import GDPRConsent, ConsentType
from app.models.audit_log import AuditLog
from app.schemas.user import GDPRConsentUpdate
from app.schemas.common import MessageResponse
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/consents", response_model=List[dict])
async def get_consents(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GDPRConsent).where(GDPRConsent.user_id == user_id))
    return [c.to_dict() for c in result.scalars().all()]

@router.post("/consents", response_model=dict)
async def update_consent(consent_data: GDPRConsentUpdate, request: Request, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GDPRConsent).where(GDPRConsent.user_id == user_id, GDPRConsent.consent_type == ConsentType(consent_data.consent_type)))
    consent = result.scalar_one_or_none()
    
    if consent:
        consent.granted = consent_data.granted
        consent.ip_address = request.client.host if request.client else None
        consent.granted_at = datetime.utcnow() if consent_data.granted else consent.granted_at
        consent.revoked_at = None if consent_data.granted else datetime.utcnow()
        consent.updated_at = datetime.utcnow()
    else:
        consent = GDPRConsent(user_id=user_id, consent_type=ConsentType(consent_data.consent_type), granted=consent_data.granted, ip_address=request.client.host if request.client else None, granted_at=datetime.utcnow() if consent_data.granted else None)
        db.add(consent)
    
    audit = AuditLog(user_id=user_id, action="consent_updated", entity_type="gdpr_consent", new_values={"consent_type": consent_data.consent_type, "granted": consent_data.granted})
    db.add(audit)
    await db.commit()
    await db.refresh(consent)
    return consent.to_dict()

@router.get("/export", response_model=dict)
async def export_data(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    
    policies = (await db.execute(select(Policy).where(Policy.user_id == user_id, Policy.is_deleted == False))).scalars().all()
    claims = (await db.execute(select(Claim).where(Claim.user_id == user_id, Claim.is_deleted == False))).scalars().all()
    payments = (await db.execute(select(Payment).where(Payment.user_id == user_id, Payment.is_deleted == False))).scalars().all()
    consents = (await db.execute(select(GDPRConsent).where(GDPRConsent.user_id == user_id))).scalars().all()
    
    audit = AuditLog(user_id=user_id, action="data_exported", entity_type="user", entity_id=user_id)
    db.add(audit)
    await db.commit()
    
    return {
        "personal_info": {"email": user.email, "full_name": user.full_name, "phone": user.phone, "created_at": user.created_at.isoformat()},
        "policies": [p.to_dict() for p in policies],
        "claims": [c.to_dict() for c in claims],
        "payments": [p.to_dict() for p in payments],
        "consents": [c.to_dict() for c in consents],
        "exported_at": datetime.utcnow().isoformat()
    }

@router.delete("/delete", response_model=MessageResponse)
async def delete_account(request: Request, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    
    user.email = f"deleted_{user_id}@anonymized.local"
    user.full_name = "DELETED USER"
    user.phone = None
    user.address = None
    user.password_hash = "DELETED"
    user.is_deleted = True
    user.is_active = False
    
    for policy in (await db.execute(select(Policy).where(Policy.user_id == user_id))).scalars().all(): policy.is_deleted = True
    for claim in (await db.execute(select(Claim).where(Claim.user_id == user_id))).scalars().all(): claim.is_deleted = True
    
    audit = AuditLog(user_id=user_id, action="account_deleted", entity_type="user", entity_id=user_id, ip_address=request.client.host if request.client else None)
    db.add(audit)
    await db.commit()
    
    return MessageResponse(success=True, message="Your account has been deleted.")

@router.get("/audit-log", response_model=List[dict])
async def get_audit_log(page: int = 1, per_page: int = 50, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditLog).where(AuditLog.user_id == user_id).order_by(AuditLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    return [l.to_dict() for l in result.scalars().all()]
