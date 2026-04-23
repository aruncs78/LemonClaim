"""
AI Chatbot (Maya) Integration Tests
Test cases: RBTES-T1297 to RBTES-T1302
"""
import pytest
from fastapi import status


class TestChatGreeting:
    """Chat Greeting Tests - RBTES-T1297"""
    
    @pytest.mark.ai
    def test_greeting_response(self, client, auth_headers):
        """
        RBTES-T1297: Greeting Response
        Verify Maya responds appropriately to greetings
        """
        # Arrange
        message_data = {"message": "Hello Maya!"}
        
        # Act
        response = client.post(
            "/api/v1/chat/message",
            json=message_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data or "message" in data
        response_text = data.get("response", data.get("message", "")).lower()
        # Maya should respond with greeting
        assert any(word in response_text for word in ["hello", "hi", "welcome", "help", "assist"])


class TestChatQuoteIntent:
    """Chat Quote Intent Tests - RBTES-T1298"""
    
    @pytest.mark.ai
    @pytest.mark.policy
    def test_quote_request_intent(self, client, auth_headers):
        """
        RBTES-T1298: Quote Request Intent
        Verify Maya understands quote request intent
        """
        # Arrange
        message_data = {"message": "I want to get a quote for home insurance"}
        
        # Act
        response = client.post(
            "/api/v1/chat/message",
            json=message_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        response_text = data.get("response", data.get("message", "")).lower()
        # Maya should recognize quote intent and ask relevant questions
        assert any(word in response_text for word in [
            "quote", "coverage", "property", "address", "insurance", "help"
        ])


class TestChatClaimAssistance:
    """Chat Claim Assistance Tests - RBTES-T1299"""
    
    @pytest.mark.ai
    @pytest.mark.claims
    def test_claim_filing_assistance(self, client, auth_headers):
        """
        RBTES-T1299: Claim Filing Assistance
        Verify Maya assists with claim filing
        """
        # Arrange
        message_data = {"message": "I need to file a claim for water damage"}
        
        # Act
        response = client.post(
            "/api/v1/chat/message",
            json=message_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        response_text = data.get("response", data.get("message", "")).lower()
        # Maya should guide through claim process
        assert any(word in response_text for word in [
            "claim", "damage", "incident", "help", "policy", "file"
        ])


class TestChatClaimStatus:
    """Chat Claim Status Tests - RBTES-T1300"""
    
    @pytest.mark.ai
    @pytest.mark.claims
    def test_claim_status_check(self, client, auth_headers, test_claim):
        """
        RBTES-T1300: Claim Status Check
        Verify Maya can check claim status
        """
        # Arrange
        message_data = {"message": f"What is the status of my claim {test_claim.claim_number}?"}
        
        # Act
        response = client.post(
            "/api/v1/chat/message",
            json=message_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        response_text = data.get("response", data.get("message", "")).lower()
        # Maya should provide status information
        assert any(word in response_text for word in [
            "status", "claim", "pending", "review", "approved", test_claim.claim_number.lower()
        ])


class TestChatHistory:
    """Chat History Tests - RBTES-T1301"""
    
    @pytest.mark.ai
    def test_chat_history_persistence(self, client, auth_headers):
        """
        RBTES-T1301: Chat History Persistence
        Verify chat history is saved and retrievable
        """
        # Arrange - Send multiple messages
        messages = [
            {"message": "Hello"},
            {"message": "I need help with insurance"}
        ]
        
        for msg in messages:
            client.post("/api/v1/chat/message", json=msg, headers=auth_headers)
        
        # Act - Get chat history
        response = client.get("/api/v1/chat/history", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least our messages


class TestChatSuggestions:
    """Chat Contextual Suggestions Tests - RBTES-T1302"""
    
    @pytest.mark.ai
    def test_contextual_suggestions(self, client, auth_headers):
        """
        RBTES-T1302: Contextual Suggestions
        Verify Maya provides contextual action suggestions
        """
        # Arrange
        message_data = {"message": "What can I do here?"}
        
        # Act
        response = client.post(
            "/api/v1/chat/message",
            json=message_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Check for suggestions in response
        response_text = data.get("response", data.get("message", "")).lower()
        suggestions = data.get("suggestions", [])
        
        # Maya should provide actionable suggestions
        has_suggestions = len(suggestions) > 0 or any(
            word in response_text for word in [
                "quote", "claim", "policy", "help", "can help", "options"
            ]
        )
        assert has_suggestions
