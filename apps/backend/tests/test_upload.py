# tests/test_upload.py

from fastapi.testclient import TestClient
import io

def test_upload_document(client: TestClient, auth_headers):
    # We'll upload a fake text file in memory
    file_content = b"Hello from a test file."
    files = {
        "file": ("test.txt", file_content, "text/plain")
    }
    response = client.post("/upload/", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["msg"] == "File uploaded"
    assert "document_id" in data