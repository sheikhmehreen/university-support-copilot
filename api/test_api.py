import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)

TICKET = {
    "student_name": "A",
    "student_id": "1",
    "email": "a@b.com",
    "department": "IT",
    "description": "test",
}
HEADERS = {"x-api-key": "test-secret"}


def fake_llm(payload):
    """Build a fake Groq response so tests never call the real API."""
    resp = MagicMock()
    resp.choices[0].message.content = json.dumps(payload)
    return resp


# --- Basic and auth tests ---

def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_classify_without_key_is_rejected():
    assert client.post("/classify", json=TICKET).status_code == 401


def test_classify_with_wrong_key_is_rejected():
    r = client.post("/classify", json=TICKET, headers={"x-api-key": "wrong-key"})
    assert r.status_code == 401


# --- LLM output tests (Groq is mocked) ---

def test_classify_valid_llm_output(monkeypatch):
    monkeypatch.setattr(main, "API_SECRET", "test-secret")
    good = {
        "category": "Fee Challan",
        "priority": "High",
        "summary": "Student cannot pay fee",
        "needs_review": False,
        "review_reason": None,
    }
    with patch.object(main.client.chat.completions, "create", return_value=fake_llm(good)):
        r = client.post("/classify", json=TICKET, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["priority"] == "High"
    assert r.json()["needs_review"] is False


def test_classify_invalid_priority_is_rejected(monkeypatch):
    monkeypatch.setattr(main, "API_SECRET", "test-secret")
    bad = {
        "category": "Fee",
        "priority": "Urgent",  # not Low, Medium or High
        "summary": "x",
        "needs_review": False,
        "review_reason": None,
    }
    with patch.object(main.client.chat.completions, "create", return_value=fake_llm(bad)):
        r = client.post("/classify", json=TICKET, headers=HEADERS)
    assert r.status_code == 502