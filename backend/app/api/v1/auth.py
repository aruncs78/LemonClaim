"""Authentication API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token, 
    create_refresh_token, decode_token, get_current_user_id,
    generate_password_reset_token, verify_password_reset_token
)
from app.models.user import User
from app.models.session import Session
from app.models.audit_log import AuditLog
from app.models.gdpr_consent import GDPRConsent, ConsentType
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    PasswordReset, PasswordResetConfirm, RefreshTokenRequest
)
from app.schemas.common import MessageResponse
from datetime import datetime, timedelta
from app.core.config import settings
import uuid
import hashlib

router = APIRouter()


def hash_token(token: str) -> str:
    """Hash a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check GDPR consent
    if not user_data.gdpr_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GDPR consent is required"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        gdpr_consent=True,
        gdpr_consent_date=datetime.utcnow()
    )
    db.add(user)
    await db.flush()
    
    # Create GDPR consent records
    for consent_type in [ConsentType.TERMS_OF_SERVICE, ConsentType.PRIVACY_POLICY, ConsentType.DATA_PROCESSING]:
        consent = GDPRConsent(
            user_id=user.id,
            consent_type=consent_type,
            granted=True,
            ip_address=request.client.host if request.client else None,
            granted_at=datetime.utcnow()
        )
        db.add(consent)
    
    # Create tokens
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    
    # Create session
    session = Session(
        user_id=user.id,
        token_hash=hash_token(access_token),
        refresh_token_hash=hash_token(refresh_token),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(session)
    
    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="user_registered",
        entity_type="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            kyc_status=user.kyc_status.value,
            gdpr_consent=user.gdpr_consent,
            mfa_enabled=user.mfa_enabled,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return tokens."""
    # Find user
    result = await db.execute(
        select(User).where(User.email == credentials.email, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Create tokens
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    
    # Create session
    session = Session(
        user_id=user.id,
        token_hash=hash_token(access_token),
        refresh_token_hash=hash_token(refresh_token),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(session)
    
    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="user_login",
        entity_type="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
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
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    # Decode refresh token
    payload = decode_token(token_data.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    
    # Find user
    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == False))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    
    # Update session
    result = await db.execute(
        select(Session).where(
            Session.user_id == user_id,
            Session.refresh_token_hash == hash_token(token_data.refresh_token),
            Session.is_active == True
        )
    )
    session = result.scalar_one_or_none()
    
    if session:
        session.token_hash = hash_token(access_token)
        session.refresh_token_hash = hash_token(refresh_token)
        session.last_activity = datetime.utcnow()
        session.expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
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
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Logout user and invalidate session."""
    # Invalidate all sessions for user (or just current one)
    result = await db.execute(
        select(Session).where(Session.user_id == user_id, Session.is_active == True)
    )
    sessions = result.scalars().all()
    
    for session in sessions:
        session.is_active = False
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="user_logout",
        entity_type="user",
        entity_id=user_id,
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    
    await db.commit()
    
    return MessageResponse(message="Successfully logged out")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if user:
        token = generate_password_reset_token(user.email)
        # TODO: Send email with reset link
        # await send_password_reset_email(user.email, token)
    
    return MessageResponse(message="If the email exists, a password reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token."""
    email = verify_password_reset_token(data.token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.password_hash = hash_password(data.new_password)
    
    # Invalidate all sessions
    result = await db.execute(select(Session).where(Session.user_id == user.id))
    sessions = result.scalars().all()
    for session in sessions:
        session.is_active = False
    
    await db.commit()
    
    return MessageResponse(message="Password has been reset successfully")
