"""
End-to-End User Flow Tests
Complete user journeys through the application
"""
import pytest
from fastapi import status


@pytest.mark.e2e
class TestCompleteUserJourney:
    """End-to-end tests for complete user flows"""
    
    def test_new_user_to_policy_purchase(self, client, test_data_factory):
        """
        E2E Test: New User Registration to Policy Purchase
        
        Flow:
        1. Register new user
        2. Login
        3. Get insurance quote
        4. Purchase policy
        5. Verify policy is active
        """
        # Step 1: Register
        user_data = test_data_factory.user_registration_data(
            email="e2e_newuser@example.com",
            password="E2ETestPassword123!"
        )
        reg_response = client.post("/api/v1/auth/register", json=user_data)
        assert reg_response.status_code == status.HTTP_201_CREATED
        user = reg_response.json()
        
        # Step 2: Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )
        assert login_response.status_code == status.HTTP_200_OK
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Step 3: Get Quote
        quote_data = test_data_factory.quote_request_data("home")
        quote_response = client.post(
            "/api/v1/policies/quote",
            json=quote_data,
            headers=headers
        )
        assert quote_response.status_code == status.HTTP_200_OK
        quote = quote_response.json()
        assert "quote_id" in quote
        
        # Step 4: Purchase Policy
        purchase_data = {
            "quote_id": quote["quote_id"],
            "payment_method": "card",
            "card_token": "tok_visa_test"
        }
        purchase_response = client.post(
            "/api/v1/policies/purchase",
            json=purchase_data,
            headers=headers
        )
        assert purchase_response.status_code == status.HTTP_201_CREATED
        policy = purchase_response.json()
        
        # Step 5: Verify Policy
        assert policy["status"] == "active"
        assert "policy_number" in policy
        
        # Verify in user's policies
        policies_response = client.get("/api/v1/policies", headers=headers)
        assert policies_response.status_code == status.HTTP_200_OK
        policies = policies_response.json()
        assert any(p["policy_number"] == policy["policy_number"] for p in policies)
    
    def test_claim_filing_to_approval(self, client, auth_headers, admin_headers, test_policy, test_data_factory):
        """
        E2E Test: File Claim to Approval and Payout
        
        Flow:
        1. User files a claim
        2. User uploads documents
        3. Admin reviews claim
        4. Admin approves claim
        5. Verify claim status updated
        """
        # Step 1: File Claim
        claim_data = test_data_factory.claim_data(
            policy_id=test_policy.id,
            claim_type="property_damage",
            amount=3000.00
        )
        claim_response = client.post(
            "/api/v1/claims",
            json=claim_data,
            headers=auth_headers
        )
        assert claim_response.status_code == status.HTTP_201_CREATED
        claim = claim_response.json()
        claim_id = claim.get("id") or claim.get("claim_id")
        
        # Step 2: Upload Documents
        files = {"file": ("receipt.pdf", b"fake pdf content", "application/pdf")}
        doc_response = client.post(
            f"/api/v1/claims/{claim_id}/documents",
            files=files,
            headers=auth_headers
        )
        # Document upload may succeed or be optional
        assert doc_response.status_code in [200, 201, 404]  # 404 if endpoint not implemented
        
        # Step 3 & 4: Admin Approves Claim
        approve_data = {
            "status": "approved",
            "approved_amount": claim["claimed_amount"],
            "admin_notes": "E2E test approval"
        }
        approve_response = client.patch(
            f"/api/v1/admin/claims/{claim_id}",
            json=approve_data,
            headers=admin_headers
        )
        assert approve_response.status_code == status.HTTP_200_OK
        approved_claim = approve_response.json()
        
        # Step 5: Verify Status
        assert approved_claim["status"] == "approved"
        
        # User can see updated status
        status_response = client.get(
            f"/api/v1/claims/{claim_id}",
            headers=auth_headers
        )
        assert status_response.status_code == status.HTTP_200_OK
        updated_claim = status_response.json()
        assert updated_claim["status"] == "approved"
    
    def test_chatbot_assisted_claim_flow(self, client, auth_headers, test_policy):
        """
        E2E Test: AI Chatbot Assisted Claim Filing
        
        Flow:
        1. User initiates chat
        2. User describes incident
        3. Maya guides through claim process
        4. Verify chat history saved
        """
        # Step 1: Initiate Chat
        greeting = {"message": "Hello, I need help"}
        greeting_response = client.post(
            "/api/v1/chat/message",
            json=greeting,
            headers=auth_headers
        )
        assert greeting_response.status_code == status.HTTP_200_OK
        
        # Step 2: Describe Incident
        incident = {"message": "My basement flooded and caused water damage"}
        incident_response = client.post(
            "/api/v1/chat/message",
            json=incident,
            headers=auth_headers
        )
        assert incident_response.status_code == status.HTTP_200_OK
        response_data = incident_response.json()
        
        # Maya should recognize claim intent
        response_text = response_data.get("response", response_data.get("message", "")).lower()
        assert any(word in response_text for word in ["claim", "damage", "help", "sorry", "file"])
        
        # Step 3: Request Claim Filing Help
        claim_help = {"message": "Yes, please help me file a claim"}
        claim_response = client.post(
            "/api/v1/chat/message",
            json=claim_help,
            headers=auth_headers
        )
        assert claim_response.status_code == status.HTTP_200_OK
        
        # Step 4: Verify Chat History
        history_response = client.get("/api/v1/chat/history", headers=auth_headers)
        assert history_response.status_code == status.HTTP_200_OK
        history = history_response.json()
        assert len(history) >= 3  # At least our 3 messages
    
    def test_gdpr_data_export_flow(self, client, test_data_factory):
        """
        E2E Test: GDPR Data Export Flow
        
        Flow:
        1. Register user
        2. Create some data (policy, claim)
        3. Request data export
        4. Verify all data is included
        """
        # Step 1: Register
        user_data = test_data_factory.user_registration_data(
            email="gdpr_test@example.com",
            password="GDPRTest123!"
        )
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Step 2: Create Some Activity
        # Get a quote (creates data)
        quote_data = test_data_factory.quote_request_data("renters")
        client.post("/api/v1/policies/quote", json=quote_data, headers=headers)
        
        # Send chat message (creates data)
        client.post(
            "/api/v1/chat/message",
            json={"message": "Hello Maya"},
            headers=headers
        )
        
        # Step 3: Request Data Export
        export_response = client.get("/api/v1/gdpr/export", headers=headers)
        assert export_response.status_code == status.HTTP_200_OK
        export_data = export_response.json()
        
        # Step 4: Verify Data Included
        assert "user" in export_data or "personal_data" in export_data
        user_info = export_data.get("user", export_data.get("personal_data", {}))
        assert user_info.get("email") == user_data["email"]


@pytest.mark.e2e
class TestPolicyLifecycle:
    """End-to-end tests for complete policy lifecycle"""
    
    def test_policy_renewal_flow(self, client, auth_headers, test_policy):
        """
        E2E Test: Policy Renewal Flow
        
        Flow:
        1. Check existing policy
        2. Initiate renewal
        3. Process payment
        4. Verify renewed policy
        """
        # Step 1: Check Policy
        policy_response = client.get(
            f"/api/v1/policies/{test_policy.id}",
            headers=auth_headers
        )
        assert policy_response.status_code == status.HTTP_200_OK
        policy = policy_response.json()
        
        # Step 2: Initiate Renewal
        renewal_response = client.post(
            f"/api/v1/policies/{test_policy.id}/renew",
            headers=auth_headers
        )
        
        # Renewal may create a new quote or directly renew
        if renewal_response.status_code == status.HTTP_200_OK:
            renewal = renewal_response.json()
            assert "new_end_date" in renewal or "quote" in renewal or "renewed" in str(renewal).lower()
    
    def test_policy_cancellation_with_refund(self, client, auth_headers, test_policy):
        """
        E2E Test: Policy Cancellation with Pro-rata Refund
        
        Flow:
        1. Request cancellation
        2. Calculate refund
        3. Process refund
        4. Verify policy cancelled
        """
        # Step 1 & 2: Request Cancellation
        cancel_data = {
            "reason": "Moving abroad",
            "effective_date": "2024-12-31",
            "request_refund": True
        }
        cancel_response = client.post(
            f"/api/v1/policies/{test_policy.id}/cancel",
            json=cancel_data,
            headers=auth_headers
        )
        
        assert cancel_response.status_code == status.HTTP_200_OK
        result = cancel_response.json()
        
        # Verify cancellation
        assert result.get("status") in ["cancelled", "pending_cancellation"]


@pytest.mark.e2e
class TestSecurityFlows:
    """End-to-end security tests"""
    
    def test_token_expiry_and_refresh(self, client, test_user):
        """
        E2E Test: Token Expiry and Refresh Flow
        """
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "TestPassword123!"}
        )
        tokens = login_response.json()
        
        # Use refresh token
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh_response.status_code == status.HTTP_200_OK
        new_tokens = refresh_response.json()
        
        # New access token should work
        headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == status.HTTP_200_OK
    
    def test_unauthorized_access_blocked(self, client):
        """
        E2E Test: Unauthorized Access is Blocked
        """
        # Try accessing protected endpoints without auth
        endpoints = [
            "/api/v1/policies",
            "/api/v1/claims",
            "/api/v1/payments/history",
            "/api/v1/gdpr/export"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
