"""API tests for investments endpoints."""
from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_create_investment() -> None:
    response = client.post(
        "/investments/",
        json={
            "name": "HDFC Flexi Cap",
            "provider": "HDFC MF",
            "type": "MF",
            "notes": "Growth fund"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "HDFC Flexi Cap"
    assert data["type"] == "MF"


def test_list_investments() -> None:
    response = client.get("/investments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_add_contribution() -> None:
    inv_response = client.post(
        "/investments/",
        json={
            "name": "Test Fund",
            "provider": "Test Provider",
            "type": "MF"
        }
    )
    investment_id = inv_response.json()["id"]
    
    response = client.post(
        "/investments/contributions",
        json={
            "investment_id": investment_id,
            "date": "2024-01-15",
            "amount": 10000.00
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert float(data["amount"]) == 10000.00


def test_add_snapshot() -> None:
    inv_response = client.post(
        "/investments/",
        json={
            "name": "Snapshot Test Fund",
            "provider": "Test Provider",
            "type": "MF"
        }
    )
    investment_id = inv_response.json()["id"]
    
    response = client.post(
        "/investments/snapshots",
        json={
            "investment_id": investment_id,
            "date": "2024-01-31",
            "current_value": 11000.00
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert float(data["current_value"]) == 11000.00


def test_get_portfolio_summary() -> None:
    response = client.get("/investments/portfolio/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_invested" in data

# Made with Bob
