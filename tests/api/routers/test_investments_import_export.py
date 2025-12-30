"""Test cases for investment import/export API endpoints"""
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.storage.db import get_connection


client = TestClient(app)


@pytest.fixture
def setup_db():
    """Setup test database"""
    conn = get_connection()
    conn.execute("DELETE FROM investment_value_snapshots")
    conn.execute("DELETE FROM investment_contributions")
    conn.execute("DELETE FROM investments")
    conn.commit()
    yield conn
    conn.execute("DELETE FROM investment_value_snapshots")
    conn.execute("DELETE FROM investment_contributions")
    conn.execute("DELETE FROM investments")
    conn.commit()
    conn.close()


def test_export_investments_empty(setup_db) -> None:
    """Test exporting investments when none exist"""
    response = client.get("/investments/export/csv")
    assert response.status_code == 200
    assert "name,provider,type,notes" in response.text


def test_export_investments_with_data(setup_db) -> None:
    """Test exporting investments with data"""
    inv_data = {
        "name": "HDFC Equity Fund",
        "provider": "HDFC",
        "type": "MF",
        "notes": "Growth fund"
    }
    
    create_response = client.post("/investments/", json=inv_data)
    assert create_response.status_code == 200
    
    export_response = client.get("/investments/export/csv")
    assert export_response.status_code == 200
    
    csv_content = export_response.text
    assert "HDFC Equity Fund" in csv_content
    assert "HDFC" in csv_content
    assert "MF" in csv_content


def test_import_investments_valid_csv(setup_db) -> None:
    """Test importing valid investments CSV"""
    csv_content = """name,provider,type,notes
HDFC Equity Fund,HDFC,MF,Growth fund
Reliance Stock,Zerodha,STOCK,Long term hold
SBI FD,SBI,FD,Fixed deposit"""
    
    response = client.post(
        "/investments/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 3
    assert len(data["errors"]) == 0
    assert data["total_rows"] == 3


def test_import_investments_invalid_type(setup_db) -> None:
    """Test importing investments with invalid type"""
    csv_content = """name,provider,type,notes
Invalid Investment,Provider,INVALID_TYPE,Test"""
    
    response = client.post(
        "/investments/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Invalid type" in data["errors"][0] or "MF, STOCK, FD, GOLD" in data["errors"][0]


def test_import_investments_missing_name(setup_db) -> None:
    """Test importing investments with missing name"""
    csv_content = """name,provider,type,notes
,HDFC,MUTUAL_FUND,Test"""
    
    response = client.post(
        "/investments/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Name is required" in data["errors"][0]


def test_import_investments_missing_provider(setup_db) -> None:
    """Test importing investments with missing provider"""
    csv_content = """name,provider,type,notes
Test Fund,,MUTUAL_FUND,Test"""
    
    response = client.post(
        "/investments/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Provider is required" in data["errors"][0]


def test_export_contributions_empty(setup_db) -> None:
    """Test exporting contributions when none exist"""
    response = client.get("/investments/contributions/export/csv")
    assert response.status_code == 200
    assert "investment_id,date,amount,notes" in response.text


def test_export_contributions_with_data(setup_db) -> None:
    """Test exporting contributions with data"""
    inv_data = {
        "name": "Test Fund",
        "provider": "Test Provider",
        "type": "MF",
        "notes": None
    }
    inv_response = client.post("/investments/", json=inv_data)
    investment_id = inv_response.json()["id"]
    
    contrib_data = {
        "investment_id": investment_id,
        "date": "2024-01-15",
        "amount": 10000.0,
        "notes": "Monthly SIP"
    }
    client.post("/investments/contributions", json=contrib_data)
    
    export_response = client.get("/investments/contributions/export/csv")
    assert export_response.status_code == 200
    
    csv_content = export_response.text
    assert investment_id in csv_content
    assert "10000" in csv_content
    assert "2024-01-15" in csv_content


def test_export_contributions_filtered_by_investment(setup_db) -> None:
    """Test exporting contributions filtered by investment ID"""
    inv1_data = {"name": "Fund 1", "provider": "Provider 1", "type": "MF", "notes": None}
    inv2_data = {"name": "Fund 2", "provider": "Provider 2", "type": "MF", "notes": None}
    
    inv1_response = client.post("/investments/", json=inv1_data)
    inv2_response = client.post("/investments/", json=inv2_data)
    
    inv1_id = inv1_response.json()["id"]
    inv2_id = inv2_response.json()["id"]
    
    client.post("/investments/contributions", json={
        "investment_id": inv1_id, "date": "2024-01-15", "amount": 5000.0, "notes": None
    })
    client.post("/investments/contributions", json={
        "investment_id": inv2_id, "date": "2024-01-15", "amount": 3000.0, "notes": None
    })
    
    export_response = client.get(f"/investments/contributions/export/csv?investment_id={inv1_id}")
    assert export_response.status_code == 200
    
    csv_content = export_response.text
    assert inv1_id in csv_content
    assert "5000" in csv_content
    assert inv2_id not in csv_content


def test_import_contributions_valid_csv(setup_db) -> None:
    """Test importing valid contributions CSV"""
    inv_data = {"name": "Test Fund", "provider": "Test", "type": "MF", "notes": None}
    inv_response = client.post("/investments/", json=inv_data)
    investment_id = inv_response.json()["id"]
    
    csv_content = f"""investment_id,date,amount,notes
{investment_id},2024-01-15,10000,Monthly SIP
{investment_id},2024-02-15,10000,Monthly SIP"""
    
    response = client.post(
        "/investments/contributions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 2
    assert len(data["errors"]) == 0


def test_import_contributions_missing_investment_id(setup_db) -> None:
    """Test importing contributions with missing investment ID"""
    csv_content = """investment_id,date,amount,notes
,2024-01-15,10000,Test"""
    
    response = client.post(
        "/investments/contributions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Investment ID is required" in data["errors"][0]


def test_import_contributions_invalid_amount(setup_db) -> None:
    """Test importing contributions with invalid amount"""
    inv_data = {"name": "Test Fund", "provider": "Test", "type": "MF", "notes": None}
    inv_response = client.post("/investments/", json=inv_data)
    investment_id = inv_response.json()["id"]
    
    csv_content = f"""investment_id,date,amount,notes
{investment_id},2024-01-15,-1000,Test"""
    
    response = client.post(
        "/investments/contributions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Amount must be positive" in data["errors"][0]


def test_import_contributions_missing_date(setup_db) -> None:
    """Test importing contributions with missing date"""
    inv_data = {"name": "Test Fund", "provider": "Test", "type": "MF", "notes": None}
    inv_response = client.post("/investments/", json=inv_data)
    investment_id = inv_response.json()["id"]
    
    csv_content = f"""investment_id,date,amount,notes
{investment_id},,10000,Test"""
    
    response = client.post(
        "/investments/contributions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Date is required" in data["errors"][0]


def test_export_import_investments_roundtrip(setup_db) -> None:
    """Test export then import maintains data integrity for investments"""
    inv_data = {
        "name": "Test Investment",
        "provider": "Test Provider",
        "type": "MF",
        "notes": "Test notes"
    }
    
    client.post("/investments/", json=inv_data)
    
    export_response = client.get("/investments/export/csv")
    csv_content = export_response.text
    
    setup_db.execute("DELETE FROM investments")
    setup_db.commit()
    
    import_response = client.post(
        "/investments/import/csv",
        json={"file_content": csv_content}
    )
    
    assert import_response.status_code == 200
    data = import_response.json()
    assert data["created"] == 1
    
    list_response = client.get("/investments/")
    investments = list_response.json()
    assert len(investments) == 1
    assert investments[0]["name"] == "Test Investment"
    assert investments[0]["provider"] == "Test Provider"


def test_export_import_contributions_roundtrip(setup_db) -> None:
    """Test export then import maintains data integrity for contributions"""
    inv_data = {"name": "Test Fund", "provider": "Test", "type": "MF", "notes": None}
    inv_response = client.post("/investments/", json=inv_data)
    investment_id = inv_response.json()["id"]
    
    contrib_data = {
        "investment_id": investment_id,
        "date": "2024-01-15",
        "amount": 10000.0,
        "notes": "Test contribution"
    }
    client.post("/investments/contributions", json=contrib_data)
    
    export_response = client.get("/investments/contributions/export/csv")
    csv_content = export_response.text
    
    setup_db.execute("DELETE FROM investment_contributions")
    setup_db.commit()
    
    import_response = client.post(
        "/investments/contributions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert import_response.status_code == 200
    data = import_response.json()
    assert data["created"] == 1
    
    list_response = client.get(f"/investments/{investment_id}/contributions")
    contributions = list_response.json()
    assert len(contributions) == 1
    assert float(contributions[0]["amount"]) == 10000.0

# Made with Bob
