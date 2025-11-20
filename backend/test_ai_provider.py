import os
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def _jwt_header():
    # This is a dummy token with {"sub": "user123"} payload using dev key
    # Header: {"alg":"HS256","typ":"JWT"}
    # Payload: {"sub":"user123"}
    # Signed with 'dev-secret-key-change-in-production'
    return {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIn0.FuVY8Odm8Xx1t6T9-6jHgNsx3Rp3XIanFkF_jN0dXl0"
    }


def test_provider_header_openai(client, monkeypatch):
    # Force openai provider even if AI_PROVIDER env changed
    monkeypatch.setenv("AI_PROVIDER", "openai")

    # Mock OpenAI provider call to avoid real API call
    from ai_providers import OpenAIProvider
    def fake_suggest_action(self, ctx):
        return type("R", (), {"data": {
            "action": "draft_reply",
            "confidence": 0.9,
            "send_permission": "draft_only",
            "reply_text": "Test reply",
            "suggested_workflow_id": None
        }})()
    monkeypatch.setattr(OpenAIProvider, "suggest_action", fake_suggest_action)

    payload = {
        "subject": "Hello",
        "body": "Body",
        "sender": "sender@example.com",
        "user_id": "user123",
        "workflow_rules": "Always reply politely"
    }
    r = client.post("/api/v1/ai/suggest-action", json=payload, headers=_jwt_header())
    assert r.status_code == 200
    data = r.json()
    assert data["action"] == "draft_reply"


def test_provider_header_claude(client, monkeypatch):
    # Simulate claude provider override header
    monkeypatch.setenv("AI_PROVIDER", "openai")  # default remains openai
    from ai_providers import ClaudeProvider
    # Mock anthropic absence or response
    def fake_suggest_action(self, ctx):
        return type("R", (), {"data": {
            "action": "archive",
            "confidence": 0.55,
            "send_permission": "needs_review",
            "reply_text": None,
            "suggested_workflow_id": None
        }})()
    monkeypatch.setattr(ClaudeProvider, "suggest_action", fake_suggest_action)

    payload = {
        "subject": "Promo",
        "body": "Buy now",
        "sender": "marketer@example.com",
        "user_id": "user123",
        "workflow_rules": "If marketing, consider archive"
    }
    r = client.post("/api/v1/ai/suggest-action", json=payload, headers={**_jwt_header(), "X-AI-Provider": "claude"})
    assert r.status_code == 200
    data = r.json()
    assert data["action"] == "archive"