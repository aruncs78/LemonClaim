"""API routes."""
from fastapi import APIRouter
from app.api.v1 import auth, users, policies, claims, payments, chat, admin, gdpr

router = APIRouter()

# Include all v1 routes
router.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/v1/users", tags=["Users"])
router.include_router(policies.router, prefix="/v1/policies", tags=["Policies"])
router.include_router(claims.router, prefix="/v1/claims", tags=["Claims"])
router.include_router(payments.router, prefix="/v1/payments", tags=["Payments"])
router.include_router(chat.router, prefix="/v1/chat", tags=["AI Chat"])
router.include_router(admin.router, prefix="/v1/admin", tags=["Admin"])
router.include_router(gdpr.router, prefix="/v1/gdpr", tags=["GDPR"])
