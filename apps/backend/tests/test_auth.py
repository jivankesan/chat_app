# tests/test_auth.py

import pytest
from fastapi.testclient import TestClient

@pytest.mark.order(1)
def test_register_new_user(client: TestClient):
    data = {"email": "test@example.com", "password": "secret123"}
    response = client.post("/auth/register", json=data)
    assert response.status_code == 200
    resp_data = response.json()
    assert "user_id" in resp_data
    assert resp_data["msg"] == "User registered successfully"

@pytest.mark.order(2)
def test_register_existing_user(client: TestClient):
    data = {"email": "test@example.com", "password": "secret123"}
    response = client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

@pytest.mark.order(3)
def test_login_success(client: TestClient):
    data = {
        "username": "test@example.com",
        "password": "secret123"
    }
    response = client.post("/auth/login", data=data)
    assert response.status_code == 200
    resp_data = response.json()
    assert "access_token" in resp_data
    assert resp_data["token_type"] == "bearer"

@pytest.mark.order(4)
def test_login_invalid_credentials(client: TestClient):
    data = {
        "username": "test@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.text