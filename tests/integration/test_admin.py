"""
Admin Dashboard Integration Tests
Test cases: RBTES-T1315 to RBTES-T1322
"""
import pytest
from fastapi import status


class TestAdminDashboard:
    """Admin Dashboard Tests - RBTES-T1315"""
    
    @pytest.mark.smoke
    @pytest.mark.admin
    def test_dashboard_statistics(self, client, admin_headers):
        """
        RBTES-T1315: Dashboard Statistics
        Verify admin can view dashboard statistics
        """
        # Act
        response = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_users" in data or "users" in data
        assert "total_policies" in data or "policies" in data
        assert "total_claims" in data or "claims" in data
        assert "revenue" in data or "total_revenue" in data


class TestAdminUserManagement:
    """Admin User Management Tests - RBTES-T1316 to RBTES-T1317"""
    
    @pytest.mark.admin
    def test_list_all_users(self, client, admin_headers):
        """
        RBTES-T1316: List All Users
        Verify admin can list all users
        """
        # Act
        response = client.get("/api/v1/admin/users", headers=admin_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list) or "users" in data
        users = data if isinstance(data, list) else data["users"]
        assert len(users) >= 1
        
        # Verify user data structure
        for user in users[:1]:
            assert "email" in user
            assert "is_active" in user
    
    @pytest.mark.admin
    def test_deactivate_user_account(self, client, admin_headers, test_user):
        """
        RBTES-T1317: Deactivate User Account
        Verify admin can deactivate a user account
        """
        # Arrange
        deactivate_data = {
            "is_active": False,
            "reason": "Account violation"
        }
        
        # Act
        response = client.patch(
            f"/api/v1/admin/users/{test_user.id}",
            json=deactivate_data,
            headers=admin_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] == False


class TestAdminClaimsManagement:
    """Admin Claims Management Tests - RBTES-T1318 to RBTES-T1320"""
    
    @pytest.mark.admin
    @pytest.mark.claims
    def test_review_pending_claims(self, client, admin_headers):
        """
        RBTES-T1318: Review Pending Claims
        Verify admin can view pending claims
        """
        # Act
        response = client.get(
            "/api/v1/admin/claims?status=pending",
            headers=admin_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list) or "claims" in data
    
    @pytest.mark.smoke
    @pytest.mark.admin
    @pytest.mark.claims
    def test_approve_claim(self, client, admin_headers, test_claim):
        """
        RBTES-T1319: Approve Claim
        Verify admin can approve a claim
        """
        # Arrange
        approve_data = {
            "status": "approved",
            "approved_amount": test_claim.claimed_amount,
            "admin_notes": "Claim verified and approved"
        }
        
        # Act
        response = client.patch(
            f"/api/v1/admin/claims/{test_claim.id}",
            json=approve_data,
            headers=admin_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "approved"
        assert data["approved_amount"] == test_claim.claimed_amount
    
    @pytest.mark.admin
    @pytest.mark.claims
    def test_reject_claim(self, client, admin_headers, test_claim):
        """
        RBTES-T1320: Reject Claim
        Verify admin can reject a claim with reason
        """
        # Arrange
        reject_data = {
            "status": "rejected",
            "rejection_reason": "Claim not covered under policy terms",
            "admin_notes": "Section 4.2 exclusion applies"
        }
        
        # Act
        response = client.patch(
            f"/api/v1/admin/claims/{test_claim.id}",
            json=reject_data,
            headers=admin_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "rejected"
        assert "rejection_reason" in data


class TestAdminAnalytics:
    """Admin Analytics Tests - RBTES-T1321"""
    
    @pytest.mark.admin
    def test_view_analytics(self, client, admin_headers):
        """
        RBTES-T1321: View Analytics
        Verify admin can view system analytics
        """
        # Act
        response = client.get("/api/v1/admin/analytics", headers=admin_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Verify analytics data structure
        assert "claims_by_status" in data or "claims" in data
        assert "revenue_trend" in data or "revenue" in data


class TestAdminAccessControl:
    """Admin Access Control Tests - RBTES-T1322"""
    
    @pytest.mark.admin
    @pytest.mark.authentication
    def test_access_denied_for_non_admin(self, client, auth_headers):
        """
        RBTES-T1322: Access Denied for Non-Admin
        Verify non-admin users cannot access admin endpoints
        """
        # Act - Try to access admin endpoint with regular user
        response = client.get("/api/v1/admin/dashboard", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "permission" in str(data["detail"]).lower() or "forbidden" in str(data["detail"]).lower() or "admin" in str(data["detail"]).lower()
    
    @pytest.mark.admin
    @pytest.mark.authentication
    def test_admin_user_list_access_denied(self, client, auth_headers):
        """
        Additional: Non-admin cannot list users
        """
        # Act
        response = client.get("/api/v1/admin/users", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.admin
    @pytest.mark.authentication
    def test_admin_claim_approval_access_denied(self, client, auth_headers, test_claim):
        """
        Additional: Non-admin cannot approve claims
        """
        # Arrange
        approve_data = {"status": "approved", "approved_amount": 1000}
        
        # Act
        response = client.patch(
            f"/api/v1/admin/claims/{test_claim.id}",
            json=approve_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
