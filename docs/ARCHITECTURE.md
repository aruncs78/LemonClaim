# LemonClaim - Insurance Application Architecture

## 📋 Executive Summary

**LemonClaim** is a modern, full-featured insurance claim application inspired by Lemonade, built with:
- **Frontend**: Next.js 14 (App Router) + Tailwind CSS + TypeScript
- **Backend**: Python FastAPI + SQLAlchemy
- **Database**: SQLite (with option to scale to PostgreSQL)
- **Cloud**: Microsoft Azure
- **AI**: Azure OpenAI for chatbot & ML models for fraud detection

---

## 🏗️ High-Level Architecture

```mermaid
flowchart TB
    subgraph Client["🖥️ Client Layer"]
        WEB[Next.js Web App]
        PWA[Progressive Web App]
    end

    subgraph Gateway["🚪 API Gateway"]
        APIM[Azure API Management]
    end

    subgraph Auth["🔐 Authentication"]
        AUTH[Custom Auth Service]
        JWT[JWT Token Manager]
        MFA[MFA Service]
    end

    subgraph Backend["⚙️ Backend Services"]
        USER[User Service]
        POLICY[Policy Service]
        CLAIMS[Claims Service]
        PAYMENT[Payment Service]
        NOTIF[Notification Service]
        GDPR[GDPR Service]
        AUDIT[Audit Service]
    end

    subgraph AI["🤖 AI Layer"]
        MAYA[Maya AI Chatbot]
        FRAUD[Fraud Detection]
        RISK[Risk Assessment]
        OCR[Document AI]
    end

    subgraph Data["💾 Data Layer"]
        SQLITE[(SQLite DB)]
        BLOB[Azure Blob Storage]
        REDIS[Redis Cache]
    end

    subgraph External["🔗 External Services"]
        STRIPE[Stripe Payments]
        SENDGRID[SendGrid Email]
        TWILIO[Twilio SMS]
    end

    Client --> Gateway
    Gateway --> Auth
    Auth --> Backend
    Backend --> AI
    Backend --> Data
    Backend --> External
```

---

## 🔄 System Flow Diagrams

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth Service
    participant DB as Database
    participant R as Redis

    U->>F: Enter credentials
    F->>A: POST /auth/login
    A->>DB: Validate user
    DB-->>A: User data
    A->>A: Verify password (bcrypt)
    A->>A: Generate JWT + Refresh Token
    A->>R: Store session
    A-->>F: Return tokens
    F->>F: Store in httpOnly cookie
    F-->>U: Redirect to dashboard
```

### Claims Processing Flow

```mermaid
sequenceDiagram
    participant U as User
    participant M as Maya AI
    participant C as Claims Service
    participant D as Document AI
    participant F as Fraud Detection
    participant P as Payment Service

    U->>M: Report incident via chat
    M->>M: Extract claim details
    M->>C: Create claim record
    U->>C: Upload documents
    C->>D: Process documents (OCR)
    D-->>C: Extracted data
    C->>F: Check for fraud
    F-->>C: Risk score
    
    alt Low Risk (Auto-Approve)
        C->>P: Process payout
        P-->>U: Instant payment
    else High Risk
        C->>C: Queue for manual review
        C-->>U: Notify pending review
    end
```

---

## 📁 Project Structure

```
lemonclaim/
├── frontend/                    # Next.js 14 Application
│   ├── src/
│   │   ├── app/                 # App Router
│   │   │   ├── (auth)/          # Auth pages (login, register)
│   │   │   ├── (dashboard)/     # Protected dashboard
│   │   │   ├── api/             # API routes (BFF)
│   │   │   ├── claims/          # Claims pages
│   │   │   ├── policies/        # Policy pages
│   │   │   └── chat/            # AI Chat interface
│   │   ├── components/
│   │   │   ├── ui/              # Shadcn/UI components
│   │   │   ├── forms/           # Form components
│   │   │   ├── layout/          # Layout components
│   │   │   └── charts/          # Chart components
│   │   ├── lib/                 # Utilities
│   │   ├── hooks/               # Custom hooks
│   │   ├── stores/              # Zustand stores
│   │   └── types/               # TypeScript types
│   ├── public/                  # Static assets
│   ├── package.json
│   ├── tailwind.config.js
│   └── next.config.js
│
├── backend/                     # Python FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── policies.py
│   │   │       ├── claims.py
│   │   │       ├── payments.py
│   │   │       ├── chat.py
│   │   │       └── admin.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── repositories/        # Data access
│   │   └── middleware/
│   ├── ai/
│   │   ├── chatbot/             # Maya AI
│   │   ├── models/              # ML models
│   │   └── document_ai/         # OCR & verification
│   ├── database/
│   │   └── migrations/          # Alembic
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
│
├── infrastructure/
│   ├── terraform/               # Azure IaC
│   ├── docker/
│   └── k8s/
│
├── docs/
└── .github/workflows/           # CI/CD
```

---

## 💾 Database Schema

```mermaid
erDiagram
    USERS ||--o{ POLICIES : has
    USERS ||--o{ CLAIMS : files
    USERS ||--o{ PAYMENTS : makes
    USERS ||--o{ SESSIONS : has
    USERS ||--o{ AUDIT_LOGS : generates
    USERS ||--o{ GDPR_CONSENTS : gives
    USERS ||--o{ NOTIFICATIONS : receives
    
    POLICIES ||--o{ CLAIMS : covers
    POLICIES ||--o{ PAYMENTS : requires
    
    CLAIMS ||--o{ DOCUMENTS : contains
    CLAIMS ||--o{ PAYMENTS : results_in
    
    USERS {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        string phone
        json address
        date date_of_birth
        enum kyc_status
        boolean gdpr_consent
        boolean is_deleted
        timestamp created_at
        timestamp updated_at
    }
    
    POLICIES {
        uuid id PK
        uuid user_id FK
        string policy_number UK
        enum policy_type
        decimal coverage_amount
        decimal premium_amount
        decimal deductible
        date start_date
        date end_date
        enum status
        json property_details
        timestamp created_at
    }
    
    CLAIMS {
        uuid id PK
        uuid policy_id FK
        uuid user_id FK
        string claim_number UK
        enum claim_type
        text description
        date incident_date
        decimal claimed_amount
        decimal approved_amount
        enum status
        json ai_assessment
        timestamp created_at
    }
    
    PAYMENTS {
        uuid id PK
        uuid user_id FK
        uuid policy_id FK
        uuid claim_id FK
        enum payment_type
        decimal amount
        string currency
        string stripe_payment_id
        enum status
        timestamp payment_date
    }
    
    DOCUMENTS {
        uuid id PK
        uuid user_id FK
        uuid claim_id FK
        enum document_type
        string file_name
        string blob_url
        string mime_type
        integer file_size
        json ocr_data
        timestamp uploaded_at
    }
    
    SESSIONS {
        uuid id PK
        uuid user_id FK
        string token_hash
        string refresh_token_hash
        json device_info
        string ip_address
        timestamp expires_at
        timestamp created_at
    }
    
    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        string entity_type
        uuid entity_id
        json old_values
        json new_values
        string ip_address
        timestamp created_at
    }
    
    GDPR_CONSENTS {
        uuid id PK
        uuid user_id FK
        enum consent_type
        boolean granted
        string ip_address
        timestamp granted_at
        timestamp revoked_at
    }
    
    NOTIFICATIONS {
        uuid id PK
        uuid user_id FK
        enum type
        enum channel
        string subject
        text content
        enum status
        timestamp sent_at
    }
    
    CHAT_HISTORY {
        uuid id PK
        uuid user_id FK
        string session_id
        enum role
        text message
        string intent
        timestamp created_at
    }
    
    QUOTES {
        uuid id PK
        uuid user_id FK
        enum quote_type
        decimal coverage
        decimal premium
        json details
        date valid_until
        timestamp created_at
    }
```

---

## 🔐 Security Architecture

### Authentication & Authorization

```mermaid
flowchart LR
    subgraph Security["Security Layers"]
        WAF[Azure WAF]
        DDOS[DDoS Protection]
        SSL[SSL/TLS]
    end

    subgraph Auth["Authentication"]
        JWT[JWT Tokens]
        REFRESH[Refresh Tokens]
        MFA[2FA/MFA]
        OAUTH[OAuth 2.0]
    end

    subgraph Access["Access Control"]
        RBAC[Role-Based Access]
        POLICY[Policy Enforcement]
        AUDIT[Audit Logging]
    end

    Security --> Auth --> Access
```

### Security Measures

| Layer | Technology | Purpose |
|-------|------------|---------|
| Network | Azure WAF | Web Application Firewall |
| Transport | TLS 1.3 | Encrypted communication |
| Authentication | JWT + Refresh | Stateless auth |
| Authorization | RBAC | Role-based permissions |
| Data at Rest | AES-256 | Database encryption |
| Secrets | Azure Key Vault | Secrets management |
| Audit | Comprehensive logging | Compliance tracking |

---

## 🔒 GDPR Compliance

### Data Subject Rights Implementation

```mermaid
flowchart TB
    subgraph Rights["GDPR Rights"]
        ACCESS[Right to Access]
        RECTIFY[Right to Rectification]
        ERASE[Right to Erasure]
        PORT[Right to Portability]
        OBJECT[Right to Object]
        CONSENT[Consent Management]
    end

    subgraph Implementation["Implementation"]
        EXPORT[Data Export API]
        DELETE[Soft Delete + Anonymize]
        AUDIT_LOG[Audit Trail]
        ENCRYPT[Encryption]
    end

    ACCESS --> EXPORT
    RECTIFY --> AUDIT_LOG
    ERASE --> DELETE
    PORT --> EXPORT
    OBJECT --> CONSENT
```

### GDPR Features

1. **Consent Management**: Granular consent tracking with timestamps
2. **Data Export**: JSON export of all user data
3. **Right to Delete**: Soft delete with anonymization
4. **Audit Trail**: Complete activity logging
5. **Data Minimization**: Only collect necessary data
6. **Encryption**: AES-256 at rest, TLS in transit
7. **Breach Notification**: Automated alerting system

---

## ☁️ Azure Infrastructure

```mermaid
flowchart TB
    subgraph Azure["Azure Cloud"]
        subgraph Network["Networking"]
            VNET[Virtual Network]
            NSG[Network Security Group]
            CDN[Azure CDN]
        end

        subgraph Compute["Compute"]
            APP[Azure App Service]
            FUNC[Azure Functions]
            CONTAINER[Container Apps]
        end

        subgraph Storage["Storage"]
            BLOB[Blob Storage]
            CACHE[Azure Cache Redis]
        end

        subgraph AI_Services["AI Services"]
            OPENAI[Azure OpenAI]
            COGNITIVE[Cognitive Services]
        end

        subgraph Monitoring["Monitoring"]
            INSIGHTS[App Insights]
            MONITOR[Azure Monitor]
            ALERTS[Alert Rules]
        end

        subgraph Security_Azure["Security"]
            KEYVAULT[Key Vault]
            DEFENDER[Defender]
        end
    end

    Network --> Compute
    Compute --> Storage
    Compute --> AI_Services
    Monitoring --> Compute
    Security_Azure --> Compute
```

### Azure Services Used

| Service | Purpose | Tier |
|---------|---------|------|
| App Service | Host Next.js & FastAPI | B2 (Production) |
| Azure CDN | Static asset delivery | Standard |
| Blob Storage | Document storage | Hot tier |
| Redis Cache | Session & API caching | Basic C0 |
| Azure OpenAI | Maya AI Chatbot | Pay-as-you-go |
| Key Vault | Secrets management | Standard |
| Application Insights | Monitoring & APM | Basic |
| API Management | API Gateway | Developer |

---

## 🔌 API Design

### RESTful Endpoints

```
Base URL: /api/v1

Authentication:
  POST   /auth/register          # User registration
  POST   /auth/login             # Login (returns JWT)
  POST   /auth/refresh           # Refresh token
  POST   /auth/logout            # Logout (invalidate session)
  POST   /auth/forgot-password   # Password reset request
  POST   /auth/reset-password    # Reset password
  POST   /auth/verify-mfa        # MFA verification

Users:
  GET    /users/me               # Get current user
  PUT    /users/me               # Update profile
  DELETE /users/me               # Delete account (GDPR)
  GET    /users/me/export        # Export data (GDPR)
  POST   /users/me/consent       # Update GDPR consent

Policies:
  GET    /policies               # List user policies
  POST   /policies               # Create new policy
  GET    /policies/:id           # Get policy details
  PUT    /policies/:id           # Update policy
  DELETE /policies/:id           # Cancel policy
  POST   /policies/quote         # Get instant quote

Claims:
  GET    /claims                 # List user claims
  POST   /claims                 # File new claim
  GET    /claims/:id             # Get claim details
  PUT    /claims/:id             # Update claim
  POST   /claims/:id/documents   # Upload documents
  GET    /claims/:id/status      # Get claim status

Payments:
  GET    /payments               # Payment history
  POST   /payments/premium       # Pay premium
  POST   /payments/setup-intent  # Stripe setup
  GET    /payments/invoices      # Get invoices

Chat:
  POST   /chat/message           # Send message to Maya AI
  GET    /chat/history           # Get chat history
  POST   /chat/feedback          # Rate AI response

Admin:
  GET    /admin/users            # List all users
  GET    /admin/claims           # List all claims
  PUT    /admin/claims/:id       # Review claim
  GET    /admin/analytics        # Dashboard data
```

### API Response Format

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  },
  "errors": null
}
```

---

## 🚀 Deployment Pipeline

```mermaid
flowchart LR
    subgraph Dev["Development"]
        CODE[Code Push]
        PR[Pull Request]
    end

    subgraph CI["CI Pipeline"]
        LINT[Lint & Format]
        TEST[Unit Tests]
        BUILD[Build]
        SCAN[Security Scan]
    end

    subgraph CD["CD Pipeline"]
        STAGING[Deploy Staging]
        E2E[E2E Tests]
        PROD[Deploy Production]
    end

    Dev --> CI --> CD
```

---

## 📊 Tech Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| **Frontend Framework** | Next.js | 14.x |
| **UI Library** | Tailwind CSS | 3.x |
| **State Management** | Zustand | 4.x |
| **API Client** | TanStack Query | 5.x |
| **Backend Framework** | FastAPI | 0.109+ |
| **ORM** | SQLAlchemy | 2.x |
| **Database** | SQLite | 3.x |
| **Cache** | Redis | 7.x |
| **AI/ML** | Azure OpenAI | GPT-4 |
| **Payments** | Stripe | Latest |
| **Email** | SendGrid | Latest |
| **SMS** | Twilio | Latest |
| **Cloud** | Microsoft Azure | - |
| **Containers** | Docker | 24.x |
| **CI/CD** | GitHub Actions | - |

---

## 🎯 Feature Roadmap

### Phase 1: MVP (Weeks 1-6)
- [x] User authentication (register, login, MFA)
- [x] Basic dashboard
- [x] Policy browsing and quotes
- [x] Simple claims filing
- [x] GDPR consent management

### Phase 2: Core Features (Weeks 7-12)
- [ ] Full policy management
- [ ] Claims processing workflow
- [ ] Document upload & storage
- [ ] Payment integration (Stripe)
- [ ] Email notifications

### Phase 3: AI Integration (Weeks 13-18)
- [ ] Maya AI chatbot
- [ ] Fraud detection ML model
- [ ] Risk assessment
- [ ] Document OCR
- [ ] Instant claim approval

### Phase 4: Polish & Scale (Weeks 19-24)
- [ ] Advanced analytics dashboard
- [ ] Mobile app (PWA)
- [ ] Performance optimization
- [ ] Security audit
- [ ] Production deployment

---

## 📞 Support

For questions about the architecture, contact the development team or raise an issue in the repository.
