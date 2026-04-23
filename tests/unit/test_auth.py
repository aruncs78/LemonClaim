"""
Authentication Unit Tests
Test cases: RBTES-T1272 to RBTES-T1280
"""
import pytest
from fastapi import status


class TestUserRegistration:
    """User Registration Tests - RBTES-T1272 to RBTES-T1275"""
    
    @pytest.mark.smoke
    @pytest.mark.authentication
    def test_user_registration_valid_data(self, client, test_data_factory):
        """
        RBTES-T1272: User Registration - Valid Data
        Verify successful user registration with valid data
        """
        # Arrange
        user_data = test_data_factory.user_registration_data(
            email="validuser@example.com",
            password="SecurePassword123!",
            full_name="Valid User"
        )
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data
    
    @pytest.mark.authentication
    def test_user_registration_invalid_email(self, client, test_data_factory):
        """
        RBTES-T1273: User Registration - Invalid Email
        Verify registration fails with invalid email format
        """
        # Arrange
        user_data = test_data_factory.user_registration_data(
            email="invalid-email-format",
            password="SecurePassword123!"
        )
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "email" in str(data["detail"]).lower()
    
    @pytest.mark.authentication
    def test_user_registration_weak_password(self, client, test_data_factory):
        """
        RBTES-T1274: User Registration - Weak Password
        Verify registration fails with weak password
        """
        # Arrange
        user_data = test_data_factory.user_registration_data(
            email="weakpass@example.com",
            password="weak"  # Too short, no special chars
        )
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "password" in str(data["detail"]).lower()
    
    @pytest.mark.authentication
    @pytest.mark.gdpr
    def test_user_registration_without_gdpr_consent(self, client, test_data_factory):
        """
        RBTES-T1275: User Registration - Without GDPR Consent
        Verify registration fails without GDPR consent
        """
        # Arrange
        user_data = {
            "email": "nogdpr@example.com",
            "password": "SecurePassword123!",
            "full_name": "No GDPR User",
            "phone": "+1555123456",
            "gdpr_consent": False
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "gdpr" in str(data["detail"]).lower() or "consent" in str(data["detail"]).lower()


class TestUserLogin:
    """User Login Tests - RBTES-T1276 to RBTES-T1277"""
    
    @pytest.mark.smoke
    @pytest.mark.authentication
    def test_user_login_valid_credentials(self, client, test_user):
        """
        RBTES-T1276: User Login - Valid Credentials
        Verify successful login with valid credentials
        """
        # Arrange
        login_data = {
            "username": test_user.email,
            "password": "TestPassword123!"
        }
        
        # Act
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.authentication
    def test_user_login_invalid_password(self, client, test_user):
        """
        RBTES-T1277: User Login - Invalid Password
        Verify login fails with incorrect password
        """
        # Arrange
        login_data = {
            "username": test_user.email,
            "password": "WrongPassword123!"
        }
        
        # Act
        response = client.post("/api/v1/auth/login", data=login_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "incorrect" in str(data["detail"]).lower() or "invalid" in str(data["detail"]).lower()


class TestUserLogout:
    """User Logout Tests - RBTES-T1278"""
    
    @pytest.mark.authentication
    def test_user_logout(self, client, auth_headers):
        """
        RBTES-T1278: User Logout
        Verify successful user logout
        """
        # Act
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in str(data).lower() or "logged out" in str(data).lower()


class TestPasswordReset:
    """Password Reset Tests - RBTES-T1279"""
    
    @pytest.mark.authentication
    def test_password_reset_request(self, client, test_user):
        """
        RBTES-T1279: Password Reset Request
        Verify password reset email is sent
        """
        # Arrange
        reset_data = {"email": test_user.email}
        
        # Act
        response = client.post("/api/v1/auth/password-reset", json=reset_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in str(data).lower() or "sent" in str(data).lower()


class TestTokenRefresh:
    """JWT Token Refresh Tests - RBTES-T1280"""
    
    @pytest.mark.authentication
    def test_jwt_token_refresh(self, client, test_user):
        """
        RBTES-T1280: JWT Token Refresh
        Verify access token can be refreshed using refresh token
        """
        # Arrange - First login to get tokens
        login_data = {
            "username": test_user.email,
            "password": "TestPassword123!"
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        tokens = login_response.json()
        refresh_token = tokens.get("refresh_token")
        
        # Act
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != tokens["access_token"]  # New token
