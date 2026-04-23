"""Policy-related schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class PolicyType(str, Enum):
    HOME = "home"
    RENTERS = "renters"
    AUTO = "auto"
    LIFE = "life"
    PET = "pet"
    TRAVEL = "travel"


class PolicyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class QuoteRequest(BaseModel):
    """Schema for requesting an insurance quote."""
    policy_type: PolicyType
    coverage_amount: float = Field(..., gt=0)
    deductible: float = Field(default=500, ge=0)
    property_details: Optional[Dict[str, Any]] = None
    
    # Home/Renters specific
    property_type: Optional[str] = None
    property_value: Optional[float] = None
    square_footage: Optional[int] = None
    year_built: Optional[int] = None
    security_system: Optional[bool] = False
    
    # Auto specific
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    vin: Optional[str] = None
    
    # Life specific
    coverage_term: Optional[int] = None  # years
    smoker: Optional[bool] = None
    
    # Pet specific
    pet_type: Optional[str] = None
    pet_breed: Optional[str] = None
    pet_age: Optional[int] = None


class QuoteResponse(BaseModel):
    """Schema for quote response."""
    id: str
    quote_number: str
    policy_type: str
    coverage_amount: float
    premium_amount: float
    deductible: float
    monthly_premium: float
    details: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    valid_until: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class PolicyCreate(BaseModel):
    """Schema for creating a policy from a quote."""
    quote_id: str
    payment_method: str = "card"
    start_date: Optional[datetime] = None


class PolicyUpdate(BaseModel):
    """Schema for updating a policy."""
    coverage_amount: Optional[float] = Field(None, gt=0)
    deductible: Optional[float] = Field(None, ge=0)
    property_details: Optional[Dict[str, Any]] = None
    beneficiaries: Optional[List[Dict[str, Any]]] = None


class PolicyResponse(BaseModel):
    """Schema for policy response."""
    id: str
    policy_number: str
    policy_type: str
    coverage_amount: float
    premium_amount: float
    deductible: float
    start_date: datetime
    end_date: datetime
    status: str
    property_details: Optional[Dict[str, Any]] = None
    beneficiaries: Optional[List[Dict[str, Any]]] = None
    claims_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class PolicySummary(BaseModel):
    """Schema for policy summary (list view)."""
    id: str
    policy_number: str
    policy_type: str
    coverage_amount: float
    premium_amount: float
    status: str
    end_date: datetime
    
    class Config:
        from_attributes = True
