"""API tests for accounts endpoints."""
from fastapi.testclient import TestClient

from app.api.main import app
from app.storage.migrations import run_migrations


client = TestClient(app)


def setup_module():
    run_migrations()


def test_create_account() -> None:
    response = client.post(
        "/accounts/",
        json={
            "name": "Test Account",
            "type": "BANK",
            "institution": "Test Bank",
            "notes": "Test notes"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Account"
    assert data["type"] == "BANK"
    assert "id" in data


def test_list_accounts() -> None:
    response = client.get("/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_transaction() -> None:
    acc_response = client.post(
        "/accounts/",
        json={
            "name": "Transaction Test Account",
            "type": "BANK",
            "institution": "Test Bank"
        }
    )
    account_id = acc_response.json()["id"]
    
    response = client.post(
        "/accounts/transactions",
        json={
            "account_id": account_id,
            "date": "2024-01-15",
            "amount": 1000.00,
            "description": "Test transaction",
            "category": "Income"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test transaction"
    assert float(data["amount"]) == 1000.00


def test_list_transactions() -> None:
    response = client.get("/accounts/transactions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# Made with Bob
