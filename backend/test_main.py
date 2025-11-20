"""Unit tests for the AI Email Automation Backend."""
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from main import (
    EmailContext,
    AIActionSuggestion,
    get_system_prompt,
    get_user_persona,
    app,
)
from fastapi.testclient import TestClient

client = TestClient(app)

# Test fixtures
VALID_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIifQ.test"
TEST_USER_ID = "test_user"


class TestEmailContextValidation:
    """Test EmailContext model validation."""
    
    def test_valid_email_context(self):
        """Test that valid email context is accepted."""
        context = EmailContext(
            subject="Test Subject",
            body="Test body content",
            sender="sender@example.com",
            user_id=TEST_USER_ID,
            workflow_rules="Auto-send if from boss",
        )
        assert context.subject == "Test Subject"
        assert context.sender == "sender@example.com"
    
    def test_email_context_empty_subject(self):
        """Test that empty subject is rejected."""
        with pytest.raises(ValidationError):
            EmailContext(
                subject="",
                body="Test body",
                sender="sender@example.com",
                user_id=TEST_USER_ID,
                workflow_rules="rules",
            )
    
    def test_email_context_whitespace_only_subject(self):
        """Test that whitespace-only subject is rejected."""
        with pytest.raises(ValidationError):
            EmailContext(
                subject="   ",
                body="Test body",
                sender="sender@example.com",
                user_id=TEST_USER_ID,
                workflow_rules="rules",
            )
    
    def test_email_context_subject_too_long(self):
        """Test that subject exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            EmailContext(
                subject="a" * 501,
                body="Test body",
                sender="sender@example.com",
                user_id=TEST_USER_ID,
                workflow_rules="rules",
            )
    
    def test_email_context_body_required(self):
        """Test that body is required."""
        with pytest.raises(ValidationError):
            EmailContext(
                subject="Test",
                body="",
                sender="sender@example.com",
                user_id=TEST_USER_ID,
                workflow_rules="rules",
            )
    
    def test_email_context_with_thread_history(self):
        """Test that thread history is optional."""
        context = EmailContext(
            subject="Test",
            body="Body",
            sender="sender@example.com",
            user_id=TEST_USER_ID,
            workflow_rules="rules",
            thread_history="Previous conversation...",
        )
        assert context.thread_history == "Previous conversation..."


class TestAIActionSuggestionValidation:
    """Test AIActionSuggestion model validation."""
    
    def test_valid_suggestion(self):
        """Test that valid suggestion is created."""
        suggestion = AIActionSuggestion(
            action="draft_reply",
            confidence=0.92,
            send_permission="draft_only",
            reply_text="Thank you for your email.",
        )
        assert suggestion.action == "draft_reply"
        assert suggestion.confidence == 0.92
    
    def test_suggestion_confidence_bounds(self):
        """Test that confidence must be between 0 and 1."""
        # Valid: boundaries
        AIActionSuggestion(
            action="archive",
            confidence=0.0,
            send_permission="needs_review",
        )
        AIActionSuggestion(
            action="archive",
            confidence=1.0,
            send_permission="needs_review",
        )
        
        # Invalid: out of bounds
        with pytest.raises(ValidationError):
            AIActionSuggestion(
                action="archive",
                confidence=1.5,
                send_permission="needs_review",
            )


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_get_user_persona(self):
        """Test user persona retrieval."""
        persona = get_user_persona(TEST_USER_ID)
        assert isinstance(persona, str)
        assert len(persona) > 0
        assert "professional" in persona.lower()
    
    def test_get_system_prompt(self):
        """Test system prompt construction."""
        workflow_rules = "If from CEO, auto-send replies"
        prompt = get_system_prompt(TEST_USER_ID, workflow_rules)
        
        assert isinstance(prompt, str)
        assert "Email Automation Agent" in prompt
        assert workflow_rules in prompt
        assert "JSON" in prompt


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_root_endpoint(self):
        """Test that root endpoint returns health status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "healthy"


class TestUserStatusEndpoint:
    """Test user status endpoint."""
    
    @patch('main.verify_jwt_token')
    def test_get_user_status_success(self, mock_verify):
        """Test successful user status retrieval."""
        mock_verify.return_value = TEST_USER_ID
        
        response = client.get(
            f"/api/v1/user/status?user_id={TEST_USER_ID}",
            headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == TEST_USER_ID
        assert "subscription_status" in data
        assert data["subscription_status"] in ["free", "pro", "expired"]
    
    @patch('main.verify_jwt_token')
    def test_get_user_status_unauthorized(self, mock_verify):
        """Test that accessing another user's status is forbidden."""
        mock_verify.return_value = "different_user"
        
        response = client.get(
            f"/api/v1/user/status?user_id={TEST_USER_ID}",
            headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"}
        )
        
        assert response.status_code == 403
        assert "Unauthorized" in response.json()["detail"]


class TestSuggestActionEndpoint:
    """Test AI action suggestion endpoint."""
    
    @patch('main.client.chat.completions.create')
    @patch('main.verify_jwt_token')
    def test_suggest_action_success(self, mock_verify, mock_openai):
        """Test successful action suggestion."""
        mock_verify.return_value = TEST_USER_ID
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.tool_calls = [
            MagicMock(
                function=MagicMock(
                    arguments='{"action": "draft_reply", "confidence": 0.9, "send_permission": "draft_only", "reply_text": "Thank you!"}'
                )
            )
        ]
        mock_openai.return_value = mock_response
        
        payload = {
            "subject": "Follow up on Q3 report",
            "body": "Can you send the Q3 report?",
            "sender": "boss@company.com",
            "user_id": TEST_USER_ID,
            "workflow_rules": "If from boss, draft a polite reply",
        }
        
        response = client.post(
            "/api/v1/ai/suggest-action",
            json=payload,
            headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "draft_reply"
        assert data["confidence"] == 0.9
        assert data["reply_text"] == "Thank you!"
    
    @patch('main.verify_jwt_token')
    def test_suggest_action_invalid_input(self, mock_verify):
        """Test that invalid input is rejected."""
        mock_verify.return_value = TEST_USER_ID
        
        # Missing required field
        payload = {
            "subject": "Test",
            "body": "",  # Empty body
            "sender": "test@example.com",
            "user_id": TEST_USER_ID,
            "workflow_rules": "rules",
        }
        
        response = client.post(
            "/api/v1/ai/suggest-action",
            json=payload,
            headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"}
        )
        
        assert response.status_code == 422  # Validation error


class TestAccountsEndpoint:
    """Test accounts management endpoint."""
    
    @patch('main.verify_jwt_token')
    def test_add_account_success(self, mock_verify):
        """Test successful account addition."""
        mock_verify.return_value = TEST_USER_ID
        
        response = client.post(
            f"/api/v1/accounts/add?user_id={TEST_USER_ID}&provider=gmail",
            headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestWorkflowsEndpoint:
    """Test workflows endpoint."""
    
    @patch('main.verify_jwt_token')
    def test_sync_workflows_success(self, mock_verify):
        """Test successful workflow sync."""
        mock_verify.return_value = TEST_USER_ID
        
        response = client.post(
            f"/api/v1/workflows/sync?user_id={TEST_USER_ID}&workflows=[]",
            headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
