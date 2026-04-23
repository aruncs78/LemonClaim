"""Claims API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.claim import Claim, ClaimType, ClaimStatus
from app.models.policy import Policy, PolicyStatus
from app.models.document import Document, DocumentType
from app.models.audit_log import AuditLog
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus
from app.schemas.claim import (
    ClaimCreate, ClaimUpdate, ClaimResponse, ClaimSummary, DocumentUpload
)
from app.schemas.common import MessageResponse
from typing import List, Optional
from datetime import datetime
import uuid
import random
import os

router = APIRouter()

# Create uploads directory
UPLOAD_DIR = "uploads/claims"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def generate_claim_number() -> str:
    """Generate a unique claim number."""
    prefix = "CLM"
    timestamp = datetime.utcnow().strftime("%y%m%d")
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    return f"{prefix}-{timestamp}-{random_part}"


def assess_claim_risk(claim_data: ClaimCreate, policy: Policy) -> dict:
    """AI assessment of claim risk."""
    risk_score = random.uniform(0.1, 0.8)
    flags = []
    
    # Check claim amount vs coverage
    if claim_data.claimed_amount > float(policy.coverage_amount) * 0.5:
        risk_score += 0.1
        flags.append("high_claim_ratio")
    
    # Check if new policy
    days_since_start = (datetime.utcnow() - policy.start_date).days
    if days_since_start < 30:
        risk_score += 0.15
        flags.append("new_policy")
    
    # Determine recommendation
    if risk_score < 0.3 and claim_data.claimed_amount < 1000:
        recommendation = "auto_approve"
    elif risk_score > 0.7:
        recommendation = "flag_for_review"
    else:
        recommendation = "standard_review"
    
    return {
        "risk_score": round(min(risk_score, 1.0), 3),
        "risk_level": "low" if risk_score < 0.3 else "medium" if risk_score < 0.7 else "high",
        "flags": flags,
        "recommendation": recommendation,
        "auto_approve_eligible": recommendation == "auto_approve"
    }


@router.post("", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def file_claim(
    claim_data: ClaimCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """File a new insurance claim."""
    # Verify policy exists and belongs to user
    result = await db.execute(
        select(Policy).where(
            Policy.id == claim_data.policy_id,
            Policy.user_id == user_id,
            Policy.status == PolicyStatus.ACTIVE,
            Policy.is_deleted == False
        )
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active policy not found"
        )
    
    # Validate claimed amount against coverage
    if claim_data.claimed_amount > float(policy.coverage_amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claimed amount exceeds policy coverage"
        )
    
    # Validate incident date
    if claim_data.incident_date > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incident date cannot be in the future"
        )
    
    if claim_data.incident_date < policy.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incident occurred before policy start date"
        )
    
    # AI risk assessment
    ai_assessment = assess_claim_risk(claim_data, policy)
    
    # Determine initial status
    initial_status = ClaimStatus.SUBMITTED
    approved_amount = None
    
    if ai_assessment["auto_approve_eligible"]:
        initial_status = ClaimStatus.APPROVED
        approved_amount = claim_data.claimed_amount
    
    # Create claim
    claim = Claim(
        policy_id=claim_data.policy_id,
        user_id=user_id,
        claim_number=generate_claim_number(),
        claim_type=ClaimType(claim_data.claim_type.value),
        description=claim_data.description,
        incident_date=claim_data.incident_date,
        incident_location=claim_data.incident_location,
        claimed_amount=claim_data.claimed_amount,
        approved_amount=approved_amount,
        status=initial_status,
        ai_assessment=ai_assessment,
        fraud_score=ai_assessment["risk_score"]
    )
    
    db.add(claim)
    
    # Create notification
    notification = Notification(
        user_id=user_id,
        notification_type=NotificationType.CLAIM_SUBMITTED,
        channel=NotificationChannel.IN_APP,
        subject="Claim Submitted",
        content=f"Your claim {claim.claim_number} has been submitted successfully.",
        status=NotificationStatus.SENT,
        sent_at=datetime.utcnow()
    )
    db.add(notification)
    
    # If auto-approved, send approval notification
    if initial_status == ClaimStatus.APPROVED:
        approval_notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.CLAIM_APPROVED,
            channel=NotificationChannel.IN_APP,
            subject="Claim Approved",
            content=f"Great news! Your claim {claim.claim_number} has been automatically approved for ${approved_amount}.",
            status=NotificationStatus.SENT,
            sent_at=datetime.utcnow()
        )
        db.add(approval_notification)
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="claim_filed",
        entity_type="claim",
        entity_id=claim.id,
        new_values=claim.to_dict()
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(claim)
    
    return ClaimResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        policy_id=claim.policy_id,
        claim_type=claim.claim_type.value,
        description=claim.description,
        incident_date=claim.incident_date,
        incident_location=claim.incident_location,
        claimed_amount=float(claim.claimed_amount),
        approved_amount=float(claim.approved_amount) if claim.approved_amount else None,
        status=claim.status.value,
        ai_assessment=claim.ai_assessment,
        fraud_score=float(claim.fraud_score) if claim.fraud_score else None,
        documents=[],
        created_at=claim.created_at
    )


@router.get("", response_model=List[ClaimSummary])
async def get_claims(
    status_filter: str = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all claims for the current user."""
    query = select(Claim).where(
        Claim.user_id == user_id,
        Claim.is_deleted == False
    )
    
    if status_filter:
        query = query.where(Claim.status == ClaimStatus(status_filter))
    
    query = query.order_by(Claim.created_at.desc())
    
    result = await db.execute(query)
    claims = result.scalars().all()
    
    return [
        ClaimSummary(
            id=c.id,
            claim_number=c.claim_number,
            claim_type=c.claim_type.value,
            claimed_amount=float(c.claimed_amount),
            status=c.status.value,
            incident_date=c.incident_date,
            created_at=c.created_at
        )
        for c in claims
    ]


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific claim."""
    result = await db.execute(
        select(Claim).where(
            Claim.id == claim_id,
            Claim.user_id == user_id,
            Claim.is_deleted == False
        )
    )
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Get documents
    docs_result = await db.execute(
        select(Document).where(
            Document.claim_id == claim_id,
            Document.is_deleted == False
        )
    )
    documents = docs_result.scalars().all()
    
    return ClaimResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        policy_id=claim.policy_id,
        claim_type=claim.claim_type.value,
        description=claim.description,
        incident_date=claim.incident_date,
        incident_location=claim.incident_location,
        claimed_amount=float(claim.claimed_amount),
        approved_amount=float(claim.approved_amount) if claim.approved_amount else None,
        status=claim.status.value,
        ai_assessment=claim.ai_assessment,
        fraud_score=float(claim.fraud_score) if claim.fraud_score else None,
        reviewer_notes=claim.reviewer_notes,
        documents=[d.to_dict() for d in documents],
        created_at=claim.created_at,
        updated_at=claim.updated_at
    )


@router.put("/{claim_id}", response_model=ClaimResponse)
async def update_claim(
    claim_id: str,
    update_data: ClaimUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update a claim (only for draft or submitted claims)."""
    result = await db.execute(
        select(Claim).where(
            Claim.id == claim_id,
            Claim.user_id == user_id,
            Claim.is_deleted == False
        )
    )
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    if claim.status not in [ClaimStatus.DRAFT, ClaimStatus.SUBMITTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update draft or submitted claims"
        )
    
    # Update fields
    old_values = claim.to_dict()
    
    if update_data.description is not None:
        claim.description = update_data.description
    if update_data.claimed_amount is not None:
        claim.claimed_amount = update_data.claimed_amount
    if update_data.incident_location is not None:
        claim.incident_location = update_data.incident_location
    if update_data.additional_info is not None:
        current_assessment = claim.ai_assessment or {}
        current_assessment["additional_info"] = update_data.additional_info
        claim.ai_assessment = current_assessment
    
    claim.updated_at = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="claim_updated",
        entity_type="claim",
        entity_id=claim_id,
        old_values=old_values,
        new_values=claim.to_dict()
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(claim)
    
    # Get documents
    docs_result = await db.execute(
        select(Document).where(Document.claim_id == claim_id, Document.is_deleted == False)
    )
    documents = docs_result.scalars().all()
    
    return ClaimResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        policy_id=claim.policy_id,
        claim_type=claim.claim_type.value,
        description=claim.description,
        incident_date=claim.incident_date,
        incident_location=claim.incident_location,
        claimed_amount=float(claim.claimed_amount),
        approved_amount=float(claim.approved_amount) if claim.approved_amount else None,
        status=claim.status.value,
        ai_assessment=claim.ai_assessment,
        fraud_score=float(claim.fraud_score) if claim.fraud_score else None,
        documents=[d.to_dict() for d in documents],
        created_at=claim.created_at,
        updated_at=claim.updated_at
    )


@router.post("/{claim_id}/documents", response_model=dict)
async def upload_document(
    claim_id: str,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document for a claim."""
    # Verify claim
    result = await db.execute(
        select(Claim).where(
            Claim.id == claim_id,
            Claim.user_id == user_id,
            Claim.is_deleted == False
        )
    )
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, GIF, PDF"
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB"
        )
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{claim_id}_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create document record
    document = Document(
        user_id=user_id,
        claim_id=claim_id,
        document_type=DocumentType(document_type),
        file_name=unique_filename,
        original_name=file.filename,
        local_path=file_path,
        mime_type=file.content_type,
        file_size=len(content)
    )
    
    db.add(document)
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="document_uploaded",
        entity_type="document",
        entity_id=document.id,
        new_values={"claim_id": claim_id, "file_name": file.filename}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(document)
    
    return document.to_dict()


@router.get("/{claim_id}/documents", response_model=List[dict])
async def get_claim_documents(
    claim_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all documents for a claim."""
    # Verify claim belongs to user
    result = await db.execute(
        select(Claim).where(
            Claim.id == claim_id,
            Claim.user_id == user_id,
            Claim.is_deleted == False
        )
    )
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Get documents
    docs_result = await db.execute(
        select(Document).where(
            Document.claim_id == claim_id,
            Document.is_deleted == False
        )
    )
    documents = docs_result.scalars().all()
    
    return [d.to_dict() for d in documents]


@router.get("/{claim_id}/timeline", response_model=List[dict])
async def get_claim_timeline(
    claim_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get claim status timeline."""
    # Verify claim
    result = await db.execute(
        select(Claim).where(
            Claim.id == claim_id,
            Claim.user_id == user_id,
            Claim.is_deleted == False
        )
    )
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Get audit logs for this claim
    audit_result = await db.execute(
        select(AuditLog).where(
            AuditLog.entity_type == "claim",
            AuditLog.entity_id == claim_id
        ).order_by(AuditLog.created_at.asc())
    )
    audits = audit_result.scalars().all()
    
    timeline = [
        {
            "status": "created",
            "timestamp": claim.created_at.isoformat(),
            "description": "Claim was filed"
        }
    ]
    
    for audit in audits:
        if audit.action == "claim_filed":
            continue
        timeline.append({
            "status": audit.action,
            "timestamp": audit.created_at.isoformat(),
            "description": audit.description or audit.action.replace("_", " ").title()
        })
    
    return timeline
