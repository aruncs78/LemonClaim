"""
Policy Management Integration Tests
Test cases: RBTES-T1281 to RBTES-T1288
"""
import pytest
from fastapi import status


class TestGetQuote:
    """Quote Generation Tests - RBTES-T1281 to RBTES-T1283"""
    
    @pytest.mark.smoke
    @pytest.mark.policy
    def test_get_quote_home_insurance(self, client, auth_headers, test_data_factory):
        """
        RBTES-T1281: Get Quote - Home Insurance
        Verify quote generation for home insurance
        """
        # Arrange
        quote_data = test_data_factory.quote_request_data("home")
        
        # Act
        response = client.post(
            "/api/v1/policies/quote",
            json=quote_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "quote_id" in data
        assert "premium_amount" in data
        assert "coverage_amount" in data
        assert data["policy_type"] == "home"
        assert data["premium_amount"] > 0
        assert "expires_at" in data
    
    @pytest.mark.policy
    def test_get_quote_renters_insurance(self, client, auth_headers, test_data_factory):
        """
        RBTES-T1282: Get Quote - Renters Insurance
        Verify quote generation for renters insurance
        """
        # Arrange
        quote_data = test_data_factory.quote_request_data("renters")
        
        # Act
        response = client.post(
            "/api/v1/policies/quote",
            json=quote_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["policy_type"] == "renters"
        assert data["premium_amount"] > 0
    
    @pytest.mark.policy
    def test_get_quote_auto_insurance(self, client, auth_headers, test_data_factory):
        """
        RBTES-T1283: Get Quote - Auto Insurance
        Verify quote generation for auto insurance
        """
        # Arrange
        quote_data = test_data_factory.quote_request_data("auto")
        
        # Act
        response = client.post(
            "/api/v1/policies/quote",
            json=quote_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["policy_type"] == "auto"
        assert data["premium_amount"] > 0


class TestPolicyPurchase:
    """Policy Purchase Tests - RBTES-T1284"""
    
    @pytest.mark.smoke
    @pytest.mark.policy
    def test_purchase_policy_from_quote(self, client, auth_headers, test_data_factory):
        """
        RBTES-T1284: Purchase Policy from Quote
        Verify successful policy purchase from a valid quote
        """
        # Arrange - First get a quote
        quote_data = test_data_factory.quote_request_data("home")
        quote_response = client.post(
            "/api/v1/policies/quote",
            json=quote_data,
            headers=auth_headers
        )
        quote = quote_response.json()
        
        # Act - Purchase the policy
        purchase_data = {
            "quote_id": quote["quote_id"],
            "payment_method": "card",
            "card_token": "tok_visa_test"
        }
        response = client.post(
            "/api/v1/policies/purchase",
            json=purchase_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "policy_number" in data
        assert data["status"] == "active"
        assert data["coverage_amount"] == quote["coverage_amount"]


class TestPolicyManagement:
    """Policy Management Tests - RBTES-T1285 to RBTES-T1287"""
    
    @pytest.mark.policy
    def test_view_active_policies(self, client, auth_headers, test_policy):
        """
        RBTES-T1285: View Active Policies
        Verify user can view their active policies
        """
        # Act
        response = client.get("/api/v1/policies", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(p["policy_number"] == test_policy.policy_number for p in data)
    
    @pytest.mark.policy
    def test_update_policy_coverage(self, client, auth_headers, test_policy):
        """
        RBTES-T1286: Update Policy Coverage
        Verify user can update policy coverage amount
        """
        # Arrange
        update_data = {
            "coverage_amount": 300000.00,
            "deductible": 1500.00
        }
        
        # Act
        response = client.patch(
            f"/api/v1/policies/{test_policy.id}",
            json=update_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["coverage_amount"] == 300000.00
        assert data["deductible"] == 1500.00
    
    @pytest.mark.policy
    def test_cancel_insurance_policy(self, client, auth_headers, test_policy):
        """
        RBTES-T1287: Cancel Insurance Policy
        Verify user can cancel their policy
        """
        # Arrange
        cancel_data = {
            "reason": "Moving to different coverage provider",
            "effective_date": "2024-12-31"
        }
        
        # Act
        response = client.post(
            f"/api/v1/policies/{test_policy.id}/cancel",
            json=cancel_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] in ["cancelled", "pending_cancellation"]


class TestQuoteExpiration:
    """Quote Expiration Tests - RBTES-T1288"""
    
    @pytest.mark.policy
    def test_quote_expiration_validation(self, client, auth_headers):
        """
        RBTES-T1288: Quote Expiration Validation
        Verify expired quotes cannot be used for purchase
        """
        # Arrange - Use an expired quote ID
        purchase_data = {
            "quote_id": "expired-quote-12345",
            "payment_method": "card",
            "card_token": "tok_visa_test"
        }
        
        # Act
        response = client.post(
            "/api/v1/policies/purchase",
            json=purchase_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_410_GONE
        ]
        data = response.json()
        assert "expired" in str(data["detail"]).lower() or "not found" in str(data["detail"]).lower()
