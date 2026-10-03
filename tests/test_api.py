from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validation():
    response = client.post("/qa", json={"question": ""})
    assert response.status_code == 422


def test_request_with_model():
    response = client.post(
        "/qa", json={"question": "What is 1+1? Answer with digit.", "model": "gemini-flash-lite-latest"}
    )
    assert response.status_code == 200
    assert "2" in response.json().get("answer", "")

