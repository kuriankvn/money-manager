"""API tests for subscriptions endpoints."""
from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_create_subscription() -> None:
    response = client.post(
        "/subscriptions/",
        json={
            "name": "Netflix",
            "type": "OTHER",
            "frequency": "MONTHLY",
            "due_day": 15,
            "expected_amount": 199.00,
            "start_date": "2024-01-01",
            "generate_instances": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Netflix"
    assert data["frequency"] == "MONTHLY"


def test_list_subscriptions() -> None:
    response = client.get("/subscriptions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_active_subscriptions() -> None:
    response = client.get("/subscriptions/active")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_due_instances() -> None:
    response = client.get("/subscriptions/instances/due")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# Made with Bob
