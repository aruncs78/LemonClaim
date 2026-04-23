# LemonClaim - Technical Specification

## 🛠️ Development Environment Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20.x LTS | Frontend runtime |
| Python | 3.11+ | Backend runtime |
| pnpm | 8.x | Package manager |
| Docker | 24.x | Containerization |
| Git | 2.x | Version control |
| VS Code | Latest | IDE (recommended) |

### Environment Variables

#### Frontend (.env.local)
```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Auth
NEXTAUTH_SECRET=your-secret-key-here
NEXTAUTH_URL=http://localhost:3000

# Stripe (Public)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx

# Feature Flags
NEXT_PUBLIC_ENABLE_AI_CHAT=true
NEXT_PUBLIC_ENABLE_MFA=true
```

#### Backend (.env)
```env
# App
APP_NAME=LemonClaim
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-32-chars-minimum

# Database
DATABASE_URL=sqlite:///./lemonclaim.db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Azure
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER_NAME=documents
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# SendGrid
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@lemonclaim.com

# Twilio
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1234567890

# GDPR
DATA_RETENTION_DAYS=365
GDPR_DPO_EMAIL=dpo@lemonclaim.com
```

---

## 📦 Frontend Specification

### Dependencies (package.json)

```json
{
  "name": "lemonclaim-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.5.0",
    "axios": "^1.6.0",
    "zod": "^3.22.0",
    "react-hook-form": "^7.49.0",
    "@hookform/resolvers": "^3.3.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-tabs": "^1.0.4",
    "lucide-react": "^0.312.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "date-fns": "^3.2.0",
    "recharts": "^2.10.0",
    "@stripe/stripe-js": "^2.4.0",
    "@stripe/react-stripe-js": "^2.4.0",
    "framer-motion": "^11.0.0",
    "sonner": "^1.4.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/react": "^18.2.0",
    "@types/node": "^20.11.0",
    "eslint": "^8.56.0",
    "eslint-config-next": "14.1.0",
    "prettier": "^3.2.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.1.0",
    "@playwright/test": "^1.41.0"
  }
}
```

### Key Frontend Components

```
src/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Landing page
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── forgot-password/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx          # Dashboard layout
│   │   ├── page.tsx            # Dashboard home
│   │   ├── policies/
│   │   │   ├── page.tsx        # List policies
│   │   │   ├── new/page.tsx    # New policy
│   │   │   └── [id]/page.tsx   # Policy details
│   │   ├── claims/
│   │   │   ├── page.tsx        # List claims
│   │   │   ├── new/page.tsx    # File claim
│   │   │   └── [id]/page.tsx   # Claim details
│   │   ├── payments/page.tsx
│   │   ├── settings/page.tsx
│   │   └── chat/page.tsx       # Maya AI chat
│   └── api/                    # API routes (BFF)
├── components/
│   ├── ui/                     # Base UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── forms/
│   │   ├── login-form.tsx
│   │   ├── register-form.tsx
│   │   ├── policy-form.tsx
│   │   └── claim-form.tsx
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   └── features/
│       ├── chat/
│       │   ├── chat-window.tsx
│       │   └── message-bubble.tsx
│       ├── policies/
│       │   ├── policy-card.tsx
│       │   └── quote-calculator.tsx
│       └── claims/
│           ├── claim-timeline.tsx
│           └── document-upload.tsx
├── lib/
│   ├── api-client.ts           # Axios instance
│   ├── utils.ts                # Utility functions
│   └── validations.ts          # Zod schemas
├── hooks/
│   ├── use-auth.ts
│   ├── use-policies.ts
│   └── use-claims.ts
├── stores/
│   ├── auth-store.ts
│   └── ui-store.ts
└── types/
    ├── api.ts
    ├── user.ts
    ├── policy.ts
    └── claim.ts
```

---

## 🐍 Backend Specification

### Dependencies (requirements.txt)

```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Database
sqlalchemy==2.0.25
alembic==1.13.1
aiosqlite==0.19.0

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# Redis
redis==5.0.1
aioredis==2.0.1

# Azure
azure-storage-blob==12.19.0
azure-identity==1.15.0
openai==1.9.0

# Payments
stripe==7.12.0

# Notifications
sendgrid==6.11.0
twilio==8.11.0

# Utilities
httpx==0.26.0
python-dateutil==2.8.2
Pillow==10.2.0
pdf2image==1.17.0
pytesseract==0.3.10

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
factory-boy==3.3.0

# Development
black==24.1.0
isort==5.13.2
flake8==7.0.0
mypy==1.8.0
```

### Backend Structure

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_router
from app.core.config import settings
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Models Structure

```python
# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    address = Column(JSON)
    date_of_birth = Column(DateTime)
    kyc_status = Column(Enum('pending', 'verified', 'rejected', name='kyc_status'), default='pending')
    gdpr_consent = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    policies = relationship("Policy", back_populates="user")
    claims = relationship("Claim", back_populates="user")
    sessions = relationship("Session", back_populates="user")
```

### Service Layer Example

```python
# app/services/claim_service.py
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.claim import Claim
from app.schemas.claim import ClaimCreate, ClaimUpdate
from app.repositories.claim_repository import ClaimRepository
from app.services.ai_service import AIService
from app.services.notification_service import NotificationService

class ClaimService:
    def __init__(
        self,
        db: AsyncSession,
        ai_service: AIService,
        notification_service: NotificationService
    ):
        self.repository = ClaimRepository(db)
        self.ai_service = ai_service
        self.notification_service = notification_service

    async def file_claim(self, user_id: UUID, data: ClaimCreate) -> Claim:
        # Create claim
        claim = await self.repository.create(user_id=user_id, **data.dict())
        
        # AI Assessment
        assessment = await self.ai_service.assess_claim(claim)
        claim.ai_assessment = assessment
        
        # Auto-approve if low risk and under threshold
        if assessment['risk_score'] < 0.3 and data.claimed_amount < 1000:
            claim.status = 'approved'
            claim.approved_amount = data.claimed_amount
        
        await self.repository.save(claim)
        
        # Notify user
        await self.notification_service.send_claim_update(claim)
        
        return claim

    async def get_user_claims(self, user_id: UUID) -> List[Claim]:
        return await self.repository.find_by_user(user_id)
```

---

## 🤖 AI Integration Specification

### Maya AI Chatbot

```python
# app/ai/chatbot/maya_agent.py
from openai import AzureOpenAI
from app.core.config import settings

SYSTEM_PROMPT = """
You are Maya, a friendly and helpful AI assistant for LemonClaim Insurance.
Your role is to:
1. Help users get insurance quotes
2. Assist with filing claims
3. Answer questions about policies
4. Provide status updates on claims

Always be empathetic, professional, and helpful.
When collecting information for claims, ask one question at a time.
If you detect potential fraud indicators, flag for human review.
"""

class MayaAgent:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )

    async def chat(self, user_message: str, conversation_history: list) -> dict:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation_history,
            {"role": "user", "content": user_message}
        ]
        
        response = self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_message = response.choices[0].message.content
        intent = self._detect_intent(user_message, assistant_message)
        
        return {
            "message": assistant_message,
            "intent": intent,
            "requires_action": intent in ["file_claim", "get_quote"]
        }

    def _detect_intent(self, user_msg: str, assistant_msg: str) -> str:
        # Simple intent detection (can be enhanced with ML)
        keywords = {
            "file_claim": ["claim", "accident", "damage", "stolen", "lost"],
            "get_quote": ["quote", "price", "cost", "coverage", "buy"],
            "check_status": ["status", "update", "where", "progress"],
            "general": []
        }
        
        for intent, words in keywords.items():
            if any(word in user_msg.lower() for word in words):
                return intent
        return "general"
```

### Fraud Detection Model

```python
# app/ai/models/fraud_detector.py
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict

class FraudDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self._load_model()

    def _load_model(self):
        # Load pre-trained model or train on historical data
        pass

    def assess_claim(self, claim_data: Dict) -> Dict:
        features = self._extract_features(claim_data)
        score = self.model.decision_function([features])[0]
        
        # Convert to risk score (0-1)
        risk_score = (1 - (score + 1) / 2)
        
        flags = self._get_risk_flags(claim_data, risk_score)
        
        return {
            "risk_score": round(risk_score, 3),
            "risk_level": self._get_risk_level(risk_score),
            "flags": flags,
            "recommendation": "auto_approve" if risk_score < 0.3 else "manual_review"
        }

    def _extract_features(self, claim_data: Dict) -> list:
        return [
            claim_data.get('claimed_amount', 0),
            claim_data.get('days_since_policy_start', 0),
            claim_data.get('previous_claims_count', 0),
            claim_data.get('hour_of_incident', 12),
            # Add more features
        ]

    def _get_risk_level(self, score: float) -> str:
        if score < 0.3:
            return "low"
        elif score < 0.7:
            return "medium"
        return "high"

    def _get_risk_flags(self, data: Dict, score: float) -> list:
        flags = []
        if data.get('claimed_amount', 0) > 10000:
            flags.append("high_claim_amount")
        if data.get('days_since_policy_start', 365) < 30:
            flags.append("new_policy")
        if data.get('previous_claims_count', 0) > 3:
            flags.append("multiple_prior_claims")
        return flags
```

---

## 🔐 Security Implementation

### Password Hashing

```python
# app/core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
```

### GDPR Service

```python
# app/services/gdpr_service.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
import json

class GDPRService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)

    async def export_user_data(self, user_id: UUID) -> dict:
        """Export all user data in JSON format (Right to Portability)"""
        user = await self.user_repo.get_with_all_relations(user_id)
        
        data = {
            "personal_info": {
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "address": user.address,
                "date_of_birth": str(user.date_of_birth),
            },
            "policies": [p.to_dict() for p in user.policies],
            "claims": [c.to_dict() for c in user.claims],
            "payments": [p.to_dict() for p in user.payments],
            "consents": [c.to_dict() for c in user.consents],
            "exported_at": datetime.utcnow().isoformat()
        }
        
        await self.audit_service.log_action(
            user_id=user_id,
            action="gdpr_data_export",
            entity_type="user",
            entity_id=user_id
        )
        
        return data

    async def delete_user_data(self, user_id: UUID) -> bool:
        """Anonymize and soft-delete user data (Right to Erasure)"""
        user = await self.user_repo.get(user_id)
        
        # Anonymize personal data
        user.email = f"deleted_{user_id}@anonymized.local"
        user.full_name = "DELETED USER"
        user.phone = None
        user.address = None
        user.date_of_birth = None
        user.is_deleted = True
        
        await self.user_repo.save(user)
        
        await self.audit_service.log_action(
            user_id=user_id,
            action="gdpr_data_deletion",
            entity_type="user",
            entity_id=user_id
        )
        
        return True
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/services/test_claim_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.claim_service import ClaimService
from app.schemas.claim import ClaimCreate

@pytest.fixture
def claim_service():
    db = AsyncMock()
    ai_service = MagicMock()
    notification_service = AsyncMock()
    return ClaimService(db, ai_service, notification_service)

@pytest.mark.asyncio
async def test_file_claim_auto_approve(claim_service):
    # Arrange
    claim_service.ai_service.assess_claim.return_value = {
        "risk_score": 0.1,
        "recommendation": "auto_approve"
    }
    
    claim_data = ClaimCreate(
        policy_id="uuid",
        claim_type="property_damage",
        description="Minor damage",
        claimed_amount=500
    )
    
    # Act
    result = await claim_service.file_claim("user_uuid", claim_data)
    
    # Assert
    assert result.status == "approved"
    assert result.approved_amount == 500
```

### E2E Tests

```typescript
// e2e/claims.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Claims Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should file a new claim', async ({ page }) => {
    await page.click('text=File a Claim');
    await page.selectOption('[name="policy"]', { index: 0 });
    await page.fill('[name="description"]', 'Water damage in kitchen');
    await page.fill('[name="amount"]', '1500');
    await page.setInputFiles('[name="documents"]', 'test-files/damage.jpg');
    await page.click('button:has-text("Submit Claim")');
    
    await expect(page.locator('.toast-success')).toContainText('Claim submitted');
    await expect(page).toHaveURL(/\/claims\/[\w-]+/);
  });
});
```

---

## 📈 Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page Load Time | < 2s | First Contentful Paint |
| API Response | < 200ms | 95th percentile |
| Database Query | < 50ms | Average query time |
| Uptime | 99.9% | Monthly availability |
| Concurrent Users | 1000+ | Simultaneous connections |

---

## 🚀 Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] CDN configured for static assets
- [ ] Redis cache warmed up
- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Backup strategy verified
- [ ] Security scan passed
- [ ] Load testing completed
- [ ] GDPR compliance verified
- [ ] Documentation updated

---

This technical specification provides a comprehensive guide for implementing the LemonClaim insurance application with all the required features and compliance requirements.
