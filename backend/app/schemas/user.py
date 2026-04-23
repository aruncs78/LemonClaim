"""User-related schemas."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    gdpr_consent: bool = False
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[Dict[str, Any]] = None
    date_of_birth: Optional[datetime] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str
    remember_me: bool = False


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    date_of_birth: Optional[datetime] = None
    kyc_status: str
    gdpr_consent: bool
    mfa_enabled: bool
    is_admin: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class ChangePassword(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


class GDPRConsentUpdate(BaseModel):
    """Schema for updating GDPR consents."""
    consent_type: str
    granted: bool


class GDPRDataExport(BaseModel):
    """Schema for GDPR data export response."""
    personal_info: Dict[str, Any]
    policies: List[Dict[str, Any]]
    claims: List[Dict[str, Any]]
    payments: List[Dict[str, Any]]
    consents: List[Dict[str, Any]]
    exported_at: datetime
