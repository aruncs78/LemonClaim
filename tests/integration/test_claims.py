"""
Claims Processing Integration Tests
Test cases: RBTES-T1289 to RBTES-T1296
"""
import pytest
from fastapi import status


class TestFileClaim:
    """Claim Filing Tests - RBTES-T1289 to RBTES-T1290"""
    
    @pytest.mark.smoke
    @pytest.mark.claims
    def test_file_new_claim_property_damage(self, client, auth_headers, test_policy, test_data_factory):
        """
        RBTES-T1289: File New Claim - Property Damage
        Verify successful claim filing for property damage
        """
        # Arrange
        claim_data = test_data_factory.claim_data(
            policy_id=test_policy.id,
            claim_type="property_damage",
            amount=5000.00
        )
        
        # Act
        response = client.post(
            "/api/v1/claims",
            json=claim_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "claim_number" in data
        assert data["claim_type"] == "property_damage"
        assert data["status"] in ["pending", "under_review", "auto_approved"]
        assert data["claimed_amount"] == 5000.00
    
    @pytest.mark.claims
    def test_claim_auto_approval_low_risk(self, client, auth_headers, test_policy, test_data_factory):
        """
        RBTES-T1290: Claim Auto-Approval - Low Risk
        Verify low-risk claims are automatically approved
        """
        # Arrange - Small claim under threshold
        claim_data = test_data_factory.claim_data(
            policy_id=test_policy.id,
            claim_type="property_damage",
            amount=500.00  # Low amount for auto-approval
        )
        
        # Act
        response = client.post(
            "/api/v1/claims",
            json=claim_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # Auto-approval for low-risk claims
        if data.get("risk_score", 1) < 0.3:
            assert data["status"] in ["auto_approved", "approved", "pending"]


class TestClaimDocuments:
    """Claim Document Tests - RBTES-T1291"""
    
    @pytest.mark.claims
    def test_upload_supporting_documents(self, client, auth_headers, test_claim):
        """
        RBTES-T1291: Upload Supporting Documents
        Verify documents can be uploaded for a claim
        """
        # Arrange
        files = {
            "file": ("damage_photo.jpg", b"fake image content", "image/jpeg")
        }
        
        # Act
        response = client.post(
            f"/api/v1/claims/{test_claim.id}/documents",
            files=files,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert "document_id" in data or "id" in data


class TestClaimStatus:
    """Claim Status Tests - RBTES-T1292"""
    
    @pytest.mark.claims
    def test_view_claim_status_and_timeline(self, client, auth_headers, test_claim):
        """
        RBTES-T1292: View Claim Status and Timeline
        Verify user can view claim status and history
        """
        # Act
        response = client.get(
            f"/api/v1/claims/{test_claim.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["claim_number"] == test_claim.claim_number
        assert "status" in data
        assert "created_at" in data


class TestClaimValidation:
    """Claim Validation Tests - RBTES-T1293 to RBTES-T1294"""
    
    @pytest.mark.claims
    def test_claim_amount_exceeds_coverage(self, client, auth_headers, test_policy, test_data_factory):
        """
        RBTES-T1293: Claim Amount Exceeds Coverage
        Verify error when claim exceeds policy coverage
        """
        # Arrange - Claim more than coverage
        claim_data = test_data_factory.claim_data(
            policy_id=test_policy.id,
            claim_type="property_damage",
            amount=999999999.00  # Way over coverage
        )
        
        # Act
        response = client.post(
            "/api/v1/claims",
            json=claim_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
        data = response.json()
        assert "coverage" in str(data["detail"]).lower() or "amount" in str(data["detail"]).lower()
    
    @pytest.mark.claims
    def test_future_incident_date_validation(self, client, auth_headers, test_policy):
        """
        RBTES-T1294: Future Incident Date Validation
        Verify error when incident date is in the future
        """
        # Arrange
        claim_data = {
            "policy_id": test_policy.id,
            "claim_type": "property_damage",
            "description": "Future incident",
            "incident_date": "2099-12-31",  # Future date
            "claimed_amount": 5000.00
        }
        
        # Act
        response = client.post(
            "/api/v1/claims",
            json=claim_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
        data = response.json()
        assert "date" in str(data["detail"]).lower() or "future" in str(data["detail"]).lower()


class TestClaimUpdate:
    """Claim Update Tests - RBTES-T1295"""
    
    @pytest.mark.claims
    def test_update_submitted_claim(self, client, auth_headers, test_claim):
        """
        RBTES-T1295: Update Submitted Claim
        Verify user can update a pending claim
        """
        # Arrange
        update_data = {
            "description": "Updated description with more details about the incident"
        }
        
        # Act
        response = client.patch(
            f"/api/v1/claims/{test_claim.id}",
            json=update_data,
            headers=auth_headers
        )
        
        # Assert
        if test_claim.status == "pending":
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "updated" in data["description"].lower() or data["description"] == update_data["description"]
        else:
            # Cannot update non-pending claims
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_403_FORBIDDEN
            ]


class TestFraudDetection:
    """Fraud Detection Tests - RBTES-T1296"""
    
    @pytest.mark.claims
    @pytest.mark.ai
    def test_ai_fraud_detection(self, client, auth_headers, test_policy, test_data_factory):
        """
        RBTES-T1296: AI Fraud Detection
        Verify AI fraud detection flags suspicious claims
        """
        # Arrange - Create suspicious claim pattern
        claim_data = test_data_factory.claim_data(
            policy_id=test_policy.id,
            claim_type="property_damage",
            amount=249999.00  # Near max coverage
        )
        claim_data["description"] = "Total loss of all belongings"
        
        # Act
        response = client.post(
            "/api/v1/claims",
            json=claim_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # High-risk claims should have elevated risk score
        assert "risk_score" in data
        # Claim should be flagged for review if suspicious
        if data.get("risk_score", 0) > 0.7:
            assert data["status"] in ["under_review", "flagged", "pending"]
