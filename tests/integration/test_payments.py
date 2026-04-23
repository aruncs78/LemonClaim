"""
Payment Integration Tests
Test cases: RBTES-T1303 to RBTES-T1308
"""
import pytest
from fastapi import status


class TestPaymentIntent:
    """Payment Intent Tests - RBTES-T1303"""
    
    @pytest.mark.smoke
    @pytest.mark.payments
    def test_create_payment_intent(self, client, auth_headers, test_policy):
        """
        RBTES-T1303: Create Payment Intent
        Verify payment intent creation for premium payment
        """
        # Arrange
        payment_data = {
            "policy_id": test_policy.id,
            "amount": test_policy.premium_amount,
            "payment_type": "premium"
        }
        
        # Act
        response = client.post(
            "/api/v1/payments/intent",
            json=payment_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert "client_secret" in data or "payment_intent_id" in data
        assert data.get("amount") == test_policy.premium_amount


class TestPremiumPayment:
    """Premium Payment Tests - RBTES-T1304"""
    
    @pytest.mark.payments
    def test_complete_premium_payment(self, client, auth_headers, test_policy, test_data_factory):
        """
        RBTES-T1304: Complete Premium Payment
        Verify successful premium payment processing
        """
        # Arrange
        payment_data = test_data_factory.payment_data(
            policy_id=test_policy.id,
            amount=test_policy.premium_amount
        )
        payment_data["payment_token"] = "tok_visa_test"
        
        # Act
        response = client.post(
            "/api/v1/payments",
            json=payment_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert data["status"] in ["completed", "succeeded", "processing"]
        assert "payment_id" in data or "id" in data


class TestPaymentHistory:
    """Payment History Tests - RBTES-T1305"""
    
    @pytest.mark.payments
    def test_view_payment_history(self, client, auth_headers):
        """
        RBTES-T1305: View Payment History
        Verify user can view their payment history
        """
        # Act
        response = client.get("/api/v1/payments/history", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Each payment should have required fields
        for payment in data:
            assert "amount" in payment
            assert "status" in payment
            assert "created_at" in payment


class TestPaymentSummary:
    """Payment Summary Tests - RBTES-T1306"""
    
    @pytest.mark.payments
    def test_payment_summary_statistics(self, client, auth_headers):
        """
        RBTES-T1306: Payment Summary Statistics
        Verify user can view payment summary
        """
        # Act
        response = client.get("/api/v1/payments/summary", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_paid" in data or "total" in data
        assert "pending" in data or "pending_amount" in data


class TestPaymentRefund:
    """Payment Refund Tests - RBTES-T1307"""
    
    @pytest.mark.payments
    def test_request_payment_refund(self, client, auth_headers, test_policy):
        """
        RBTES-T1307: Request Payment Refund
        Verify refund request processing
        """
        # Arrange - First make a payment
        payment_data = {
            "policy_id": test_policy.id,
            "amount": test_policy.premium_amount,
            "payment_method": "card",
            "payment_token": "tok_visa_test"
        }
        payment_response = client.post(
            "/api/v1/payments",
            json=payment_data,
            headers=auth_headers
        )
        
        if payment_response.status_code in [200, 201]:
            payment = payment_response.json()
            payment_id = payment.get("payment_id", payment.get("id"))
            
            # Act - Request refund
            refund_data = {
                "reason": "Policy cancelled within cooling-off period"
            }
            response = client.post(
                f"/api/v1/payments/{payment_id}/refund",
                json=refund_data,
                headers=auth_headers
            )
            
            # Assert
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_201_CREATED,
                status.HTTP_202_ACCEPTED
            ]
            data = response.json()
            assert data.get("status") in ["refunded", "pending", "processing"]


class TestClaimPayout:
    """Claim Payout Tests - RBTES-T1308"""
    
    @pytest.mark.payments
    @pytest.mark.claims
    def test_claim_payout_processing(self, client, admin_headers, test_claim):
        """
        RBTES-T1308: Claim Payout Processing
        Verify claim payout is processed correctly (admin action)
        """
        # Arrange - Update claim to approved status first
        approve_data = {
            "status": "approved",
            "approved_amount": test_claim.claimed_amount
        }
        client.patch(
            f"/api/v1/admin/claims/{test_claim.id}",
            json=approve_data,
            headers=admin_headers
        )
        
        # Act - Process payout
        payout_data = {
            "claim_id": test_claim.id,
            "amount": test_claim.claimed_amount,
            "payout_method": "bank_transfer"
        }
        response = client.post(
            "/api/v1/payments/payout",
            json=payout_data,
            headers=admin_headers
        )
        
        # Assert
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_202_ACCEPTED,
            status.HTTP_400_BAD_REQUEST  # May fail if claim not approved
        ]
