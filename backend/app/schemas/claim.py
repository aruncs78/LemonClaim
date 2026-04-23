"""Claim-related schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ClaimType(str, Enum):
    PROPERTY_DAMAGE = "property_damage"
    THEFT = "theft"
    WATER_DAMAGE = "water_damage"
    FIRE_DAMAGE = "fire_damage"
    LIABILITY = "liability"
    MEDICAL = "medical"
    ACCIDENT = "accident"
    NATURAL_DISASTER = "natural_disaster"
    OTHER = "other"


class ClaimStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    CLOSED = "closed"


class ClaimCreate(BaseModel):
    """Schema for creating a claim."""
    policy_id: str
    claim_type: ClaimType
    description: str = Field(..., min_length=10, max_length=5000)
    incident_date: datetime
    incident_location: Optional[Dict[str, Any]] = None
    claimed_amount: float = Field(..., gt=0)
    
    # Additional details collected via chat
    witnesses: Optional[List[Dict[str, str]]] = None
    police_report_number: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class ClaimUpdate(BaseModel):
    """Schema for updating a claim."""
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    claimed_amount: Optional[float] = Field(None, gt=0)
    incident_location: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None


class ClaimReview(BaseModel):
    """Schema for admin claim review."""
    status: ClaimStatus
    approved_amount: Optional[float] = None
    reviewer_notes: Optional[str] = None


class ClaimResponse(BaseModel):
    """Schema for claim response."""
    id: str
    claim_number: str
    policy_id: str
    claim_type: str
    description: str
    incident_date: datetime
    incident_location: Optional[Dict[str, Any]] = None
    claimed_amount: float
    approved_amount: Optional[float] = None
    status: str
    ai_assessment: Optional[Dict[str, Any]] = None
    fraud_score: Optional[float] = None
    reviewer_notes: Optional[str] = None
    documents: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ClaimSummary(BaseModel):
    """Schema for claim summary (list view)."""
    id: str
    claim_number: str
    claim_type: str
    claimed_amount: float
    status: str
    incident_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClaimTimeline(BaseModel):
    """Schema for claim status timeline."""
    status: str
    timestamp: datetime
    description: str
    actor: Optional[str] = None


class DocumentUpload(BaseModel):
    """Schema for document upload metadata."""
    document_type: str
    description: Optional[str] = None
