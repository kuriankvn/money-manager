"""Test cases for subscription import/export API endpoints"""
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.storage.db import get_connection


client = TestClient(app)


@pytest.fixture
def setup_db():
    """Setup test database"""
    conn = get_connection()
    conn.execute("DELETE FROM subscription_instances")
    conn.execute("DELETE FROM subscriptions")
    conn.commit()
    yield conn
    conn.execute("DELETE FROM subscription_instances")
    conn.execute("DELETE FROM subscriptions")
    conn.commit()
    conn.close()


def test_export_subscriptions_empty(setup_db) -> None:
    """Test exporting subscriptions when none exist"""
    response = client.get("/subscriptions/export/csv")
    assert response.status_code == 200
    assert "name,type,frequency,due_day,expected_amount,start_date,end_date,notes" in response.text


def test_export_subscriptions_with_data(setup_db) -> None:
    """Test exporting subscriptions with data"""
    sub_data = {
        "name": "Netflix",
        "type": "BILL",
        "frequency": "MONTHLY",
        "due_day": 15,
        "expected_amount": 999.0,
        "start_date": "2024-01-01",
        "end_date": None,
        "notes": "Streaming service",
        "generate_instances": False
    }
    
    create_response = client.post("/subscriptions/", json=sub_data)
    assert create_response.status_code == 200
    
    export_response = client.get("/subscriptions/export/csv")
    assert export_response.status_code == 200
    
    csv_content = export_response.text
    assert "Netflix" in csv_content
    assert "BILL" in csv_content
    assert "MONTHLY" in csv_content
    assert "999" in csv_content


def test_import_subscriptions_valid_csv(setup_db) -> None:
    """Test importing valid subscriptions CSV"""
    csv_content = """name,type,frequency,due_day,expected_amount,start_date,end_date,notes
Netflix,BILL,MONTHLY,15,999,2024-01-01,,Streaming service
Amazon Prime,BILL,YEARLY,1,1499,2024-01-01,,Prime membership"""
    
    response = client.post(
        "/subscriptions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 2
    assert len(data["errors"]) == 0
    assert data["total_rows"] == 2


def test_import_subscriptions_invalid_type(setup_db) -> None:
    """Test importing subscriptions with invalid type"""
    csv_content = """name,type,frequency,due_day,expected_amount,start_date,end_date,notes
Invalid Sub,INVALID_TYPE,MONTHLY,15,999,2024-01-01,,Test"""
    
    response = client.post(
        "/subscriptions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Invalid type" in data["errors"][0]


def test_import_subscriptions_missing_required_field(setup_db) -> None:
    """Test importing subscriptions with missing required field"""
    csv_content = """name,type,frequency,due_day,expected_amount,start_date,end_date,notes
,BILL,MONTHLY,15,999,2024-01-01,,Test"""
    
    response = client.post(
        "/subscriptions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Name is required" in data["errors"][0]


def test_import_subscriptions_invalid_due_day(setup_db) -> None:
    """Test importing subscriptions with invalid due day"""
    csv_content = """name,type,frequency,due_day,expected_amount,start_date,end_date,notes
Test Sub,BILL,MONTHLY,35,999,2024-01-01,,Test"""
    
    response = client.post(
        "/subscriptions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Due day must be between 1 and 31" in data["errors"][0]


def test_import_subscriptions_negative_amount(setup_db) -> None:
    """Test importing subscriptions with negative amount"""
    csv_content = """name,type,frequency,due_day,expected_amount,start_date,end_date,notes
Test Sub,BILL,MONTHLY,15,-999,2024-01-01,,Test"""
    
    response = client.post(
        "/subscriptions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Expected amount must be positive" in data["errors"][0]


def test_import_subscriptions_mixed_valid_invalid(setup_db) -> None:
    """Test importing mix of valid and invalid subscriptions"""
    csv_content = """name,type,frequency,due_day,expected_amount,start_date,end_date,notes
Valid Sub,BILL,MONTHLY,15,999,2024-01-01,,Valid
,BILL,MONTHLY,15,999,2024-01-01,,Invalid - no name
Another Valid,INSURANCE,MONTHLY,1,5000,2024-01-01,,Valid insurance"""
    
    response = client.post(
        "/subscriptions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 2
    assert len(data["errors"]) == 1
    assert data["total_rows"] == 3


def test_export_import_roundtrip(setup_db) -> None:
    """Test export then import maintains data integrity"""
    sub_data = {
        "name": "Test Subscription",
        "type": "BILL",
        "frequency": "MONTHLY",
        "due_day": 10,
        "expected_amount": 1500.0,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "notes": "Test notes",
        "generate_instances": False
    }
    
    client.post("/subscriptions/", json=sub_data)
    
    export_response = client.get("/subscriptions/export/csv")
    csv_content = export_response.text
    
    setup_db.execute("DELETE FROM subscriptions")
    setup_db.commit()
    
    import_response = client.post(
        "/subscriptions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert import_response.status_code == 200
    data = import_response.json()
    assert data["created"] == 1
    
    list_response = client.get("/subscriptions/")
    subscriptions = list_response.json()
    assert len(subscriptions) == 1
    assert subscriptions[0]["name"] == "Test Subscription"
    assert float(subscriptions[0]["expected_amount"]) == 1500.0

# Made with Bob
