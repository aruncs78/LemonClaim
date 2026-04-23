# 🍋 LemonClaim - Modern Insurance Application

A full-featured insurance claim application inspired by Lemonade, built with modern technologies and AI-powered features.

![LemonClaim](https://img.shields.io/badge/LemonClaim-Insurance-FF6B9D)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)

## ✨ Features

### 🏠 Insurance Products
- **Home Insurance** - Protect your home
- **Renters Insurance** - Coverage for renters
- **Auto Insurance** - Vehicle protection
- **Life Insurance** - Family security
- **Pet Insurance** - Care for your furry friends

### 🤖 AI-Powered
- **Maya AI Chatbot** - Conversational insurance assistant
- **Instant Quotes** - AI-calculated pricing
- **Fraud Detection** - ML-based risk assessment
- **Auto-Approval** - Smart claim processing

### 🔒 Security & Compliance
- **GDPR Ready** - Full compliance with data protection
- **Custom Authentication** - JWT with refresh tokens
- **MFA Support** - Two-factor authentication
- **Audit Logging** - Complete activity tracking

### 💳 Payments
- **Stripe Integration** - Secure payments
- **Subscription Management** - Recurring billing
- **Instant Payouts** - Fast claim settlements

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 14)                   │
│                    Tailwind CSS + TypeScript                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway (Azure APIM)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Python FastAPI)                  │
│         SQLAlchemy ORM │ Pydantic │ JWT Auth                │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   SQLite    │      │    Redis    │      │ Azure Blob  │
│  Database   │      │    Cache    │      │   Storage   │
└─────────────┘      └─────────────┘      └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 20.x
- Python 3.11+
- pnpm (recommended) or npm

### Backend Setup

```bash
# Navigate to backend
cd lemonclaim/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run migrations (creates SQLite database)
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# Start the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd lemonclaim/frontend

# Install dependencies
pnpm install  # or npm install

# Create .env.local file
cp .env.example .env.local

# Start development server
pnpm dev  # or npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

## 📁 Project Structure

```
lemonclaim/
├── frontend/                 # Next.js 14 Application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   ├── lib/             # Utilities & API client
│   │   ├── stores/          # Zustand stores
│   │   └── types/           # TypeScript types
│   └── package.json
│
├── backend/                  # Python FastAPI
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── core/            # Config, security, database
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── main.py
│   └── requirements.txt
│
└── docs/                     # Documentation
    ├── ARCHITECTURE.md
    └── TECH_SPEC.md
```

## 🔌 API Endpoints

### Authentication
```
POST /api/v1/auth/register    # User registration
POST /api/v1/auth/login       # User login
POST /api/v1/auth/refresh     # Refresh token
POST /api/v1/auth/logout      # Logout
```

### Policies
```
GET  /api/v1/policies         # List policies
POST /api/v1/policies         # Create policy
POST /api/v1/policies/quote   # Get quote
GET  /api/v1/policies/:id     # Get policy
```

### Claims
```
GET  /api/v1/claims           # List claims
POST /api/v1/claims           # File claim
GET  /api/v1/claims/:id       # Get claim
POST /api/v1/claims/:id/documents  # Upload docs
```

### AI Chat
```
POST /api/v1/chat/message     # Send message
GET  /api/v1/chat/history     # Get history
```

### GDPR
```
GET  /api/v1/gdpr/export      # Export data
DELETE /api/v1/gdpr/delete    # Delete account
```

## 🔐 Environment Variables

### Backend (.env)
```env
APP_NAME=LemonClaim
DEBUG=true
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite+aiosqlite:///./lemonclaim.db
JWT_SECRET_KEY=your-jwt-secret
STRIPE_SECRET_KEY=sk_test_xxx
AZURE_OPENAI_API_KEY=xxx
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
pnpm test
```

## 🚢 Deployment

### Docker
```bash
docker-compose up -d
```

### Azure
See `infrastructure/terraform/` for Azure deployment scripts.

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Technical Specification](docs/TECH_SPEC.md)
- [API Documentation](http://localhost:8000/api/docs)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Lemonade](https://www.lemonade.com/)
- Built with [Next.js](https://nextjs.org/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)

---

Made with 💗 by the LemonClaim Team
