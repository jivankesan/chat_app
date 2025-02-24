# tests/test_chat.py

import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def auth_headers(client: TestClient):
    """
    Logs in the user we created in test_auth and returns a dict of headers
    with the Bearer token. Adjust credentials if needed.
    """
    data = {"username": "test@example.com", "password": "secret123"}
    response = client.post("/auth/login", data=data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_start_chat(client: TestClient, auth_headers):
    payload = {"session_name": "My First Chat Session"}
    response = client.post("/chat/start_chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_name"] == "My First Chat Session"

def test_get_user_chats(client: TestClient, auth_headers):
    response = client.get("/chat/sessions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "session_id" in data[0]
    assert "session_name" in data[0]

def test_send_chat_message(client: TestClient, auth_headers):
    # We need an existing session_id
    sessions_resp = client.get("/chat/sessions", headers=auth_headers)
    session_id = sessions_resp.json()[0]["session_id"]

    payload = {
        "session_id": session_id,
        "message": "Hello, Assistant!",
        "model_name": "gpt-3.5-turbo"
    }
    response = client.post("/chat/send_message", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert "assistant_response" in response.json()

def test_get_chat_messages(client: TestClient, auth_headers):
    # We need an existing session_id
    sessions_resp = client.get("/chat/sessions", headers=auth_headers)
    session_id = sessions_resp.json()[0]["session_id"]

    response = client.get(f"/chat/messages/{session_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should contain both "user" and "assistant" messages
    assert len(data) >= 2
    roles = [msg["role"] for msg in data]
    assert "user" in roles
    assert "assistant" in roles