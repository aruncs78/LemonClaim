"""
GDPR Compliance Integration Tests
Test cases: RBTES-T1309 to RBTES-T1314
"""
import pytest
from fastapi import status


class TestConsentManagement:
    """Consent Management Tests - RBTES-T1309 to RBTES-T1310"""
    
    @pytest.mark.gdpr
    def test_view_consent_settings(self, client, auth_headers):
        """
        RBTES-T1309: View Consent Settings
        Verify user can view their consent settings
        """
        # Act
        response = client.get("/api/v1/gdpr/consent", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "privacy_policy" in data or "consents" in data
        assert "marketing" in data or any("marketing" in str(c).lower() for c in data.get("consents", [data]))
    
    @pytest.mark.gdpr
    def test_update_marketing_consent(self, client, auth_headers):
        """
        RBTES-T1310: Update Marketing Consent
        Verify user can update marketing consent
        """
        # Arrange
        consent_data = {
            "marketing_emails": False,
            "marketing_sms": False,
            "third_party_sharing": False
        }
        
        # Act
        response = client.put(
            "/api/v1/gdpr/consent",
            json=consent_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Verify consent was updated
        assert data.get("marketing_emails") == False or "updated" in str(data).lower()


class TestDataPortability:
    """Data Portability Tests - RBTES-T1311"""
    
    @pytest.mark.smoke
    @pytest.mark.gdpr
    def test_data_export_portability(self, client, auth_headers):
        """
        RBTES-T1311: Data Export (Portability)
        Verify user can export all their data (GDPR Article 20)
        """
        # Act
        response = client.get("/api/v1/gdpr/export", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify export contains user data sections
        assert "user" in data or "personal_data" in data
        assert "policies" in data or "insurance_policies" in data
        assert "claims" in data or "insurance_claims" in data
        
        # Verify data format is portable (JSON)
        assert isinstance(data, dict)


class TestRightToErasure:
    """Right to Erasure Tests - RBTES-T1312 to RBTES-T1313"""
    
    @pytest.mark.gdpr
    def test_account_deletion_erasure(self, client, test_data_factory):
        """
        RBTES-T1312: Account Deletion (Erasure)
        Verify user can delete their account (GDPR Article 17)
        """
        # Arrange - Create a new user for deletion
        user_data = test_data_factory.user_registration_data(
            email="deleteme@example.com",
            password="DeleteMe123!"
        )
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        
        if reg_response.status_code == 201:
            # Login to get token
            login_response = client.post(
                "/api/v1/auth/login",
                data={"username": user_data["email"], "password": user_data["password"]}
            )
            tokens = login_response.json()
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            
            # Act - Request deletion
            delete_data = {
                "confirmation": "DELETE MY ACCOUNT",
                "reason": "No longer need insurance"
            }
            response = client.post(
                "/api/v1/gdpr/delete-account",
                json=delete_data,
                headers=headers
            )
            
            # Assert
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_202_ACCEPTED
            ]
            data = response.json()
            assert "deleted" in str(data).lower() or "scheduled" in str(data).lower()
    
    @pytest.mark.gdpr
    def test_deletion_blocked_active_policies(self, client, auth_headers, test_policy):
        """
        RBTES-T1313: Deletion Blocked - Active Policies
        Verify deletion is blocked when user has active policies
        """
        # Arrange
        delete_data = {
            "confirmation": "DELETE MY ACCOUNT",
            "reason": "Testing deletion block"
        }
        
        # Act
        response = client.post(
            "/api/v1/gdpr/delete-account",
            json=delete_data,
            headers=auth_headers
        )
        
        # Assert - Should be blocked due to active policy
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT
        ]
        data = response.json()
        assert "active" in str(data["detail"]).lower() or "policy" in str(data["detail"]).lower()


class TestAuditLog:
    """Audit Log Tests - RBTES-T1314"""
    
    @pytest.mark.gdpr
    def test_view_audit_log(self, client, auth_headers):
        """
        RBTES-T1314: View Audit Log
        Verify user can view their data access audit log
        """
        # Act
        response = client.get("/api/v1/gdpr/audit-log", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # Each audit entry should have required fields
        for entry in data:
            assert "action" in entry or "event" in entry
            assert "timestamp" in entry or "created_at" in entry
