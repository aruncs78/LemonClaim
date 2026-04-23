"""
LemonClaim Test Configuration
Pytest fixtures and test utilities
"""
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.policy import Policy
from app.models.claim import Claim

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator:
    """Create a fresh database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client() -> Generator:
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session) -> User:
    """Create a test user"""
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        full_name="Test User",
        phone="+1234567890",
        is_active=True,
        is_verified=True,
        gdpr_consent=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session) -> User:
    """Create a test admin user"""
    admin = User(
        email="admin@lemonclaim.com",
        hashed_password=get_password_hash("AdminPassword123!"),
        full_name="Admin User",
        phone="+1987654321",
        is_active=True,
        is_verified=True,
        is_admin=True,
        gdpr_consent=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(test_user) -> Dict[str, str]:
    """Generate authentication headers for test user"""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(test_admin) -> Dict[str, str]:
    """Generate authentication headers for admin user"""
    token = create_access_token(data={"sub": test_admin.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_policy(db_session, test_user) -> Policy:
    """Create a test policy"""
    policy = Policy(
        user_id=test_user.id,
        policy_number="POL-TEST-001",
        policy_type="home",
        status="active",
        coverage_amount=250000.00,
        premium_amount=125.00,
        deductible=1000.00,
        start_date="2024-01-01",
        end_date="2025-01-01",
        property_address="123 Test Street, Test City, TC 12345"
    )
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    return policy


@pytest.fixture
def test_claim(db_session, test_user, test_policy) -> Claim:
    """Create a test claim"""
    claim = Claim(
        user_id=test_user.id,
        policy_id=test_policy.id,
        claim_number="CLM-TEST-001",
        claim_type="property_damage",
        status="pending",
        description="Water damage from burst pipe",
        incident_date="2024-06-15",
        claimed_amount=5000.00,
        risk_score=0.2
    )
    db_session.add(claim)
    db_session.commit()
    db_session.refresh(claim)
    return claim


# Test data generators
class TestDataFactory:
    """Factory for generating test data"""
    
    @staticmethod
    def user_registration_data(
        email: str = "newuser@example.com",
        password: str = "SecurePassword123!",
        full_name: str = "New User"
    ) -> Dict[str, Any]:
        return {
            "email": email,
            "password": password,
            "full_name": full_name,
            "phone": "+1555123456",
            "gdpr_consent": True
        }
    
    @staticmethod
    def quote_request_data(policy_type: str = "home") -> Dict[str, Any]:
        if policy_type == "home":
            return {
                "policy_type": "home",
                "coverage_amount": 300000,
                "property_address": "456 Main St, City, ST 12345",
                "property_type": "single_family",
                "year_built": 2010
            }
        elif policy_type == "auto":
            return {
                "policy_type": "auto",
                "coverage_amount": 50000,
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": 2022
            }
        elif policy_type == "renters":
            return {
                "policy_type": "renters",
                "coverage_amount": 30000,
                "property_address": "789 Apt Blvd, City, ST 12345"
            }
        return {}
    
    @staticmethod
    def claim_data(
        policy_id: int,
        claim_type: str = "property_damage",
        amount: float = 5000.00
    ) -> Dict[str, Any]:
        return {
            "policy_id": policy_id,
            "claim_type": claim_type,
            "description": "Test claim description with detailed incident report",
            "incident_date": "2024-06-15",
            "claimed_amount": amount
        }
    
    @staticmethod
    def payment_data(
        policy_id: int,
        amount: float = 125.00
    ) -> Dict[str, Any]:
        return {
            "policy_id": policy_id,
            "amount": amount,
            "payment_method": "card",
            "card_last_four": "4242"
        }


@pytest.fixture
def test_data_factory() -> TestDataFactory:
    """Provide test data factory"""
    return TestDataFactory()


# Markers for test categorization
def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "authentication: mark test as authentication test")
    config.addinivalue_line("markers", "policy: mark test as policy test")
    config.addinivalue_line("markers", "claims: mark test as claims test")
    config.addinivalue_line("markers", "payments: mark test as payment test")
    config.addinivalue_line("markers", "gdpr: mark test as GDPR test")
    config.addinivalue_line("markers", "admin: mark test as admin test")
    config.addinivalue_line("markers", "ai: mark test as AI/chatbot test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
