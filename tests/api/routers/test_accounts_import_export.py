"""Test cases for transaction import/export API endpoints"""
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.storage.db import get_connection


client = TestClient(app)


@pytest.fixture
def setup_db():
    """Setup test database"""
    conn = get_connection()
    conn.execute("DELETE FROM transactions")
    conn.execute("DELETE FROM accounts")
    conn.commit()
    yield conn
    conn.execute("DELETE FROM transactions")
    conn.execute("DELETE FROM accounts")
    conn.commit()
    conn.close()


@pytest.fixture
def create_test_account(setup_db):
    """Create a test account"""
    account_data = {
        "name": "Test Bank Account",
        "type": "BANK",
        "institution": "Test Bank",
        "notes": "Test account"
    }
    response = client.post("/accounts/", json=account_data)
    assert response.status_code == 200
    return response.json()["id"]


def test_export_transactions_empty(setup_db) -> None:
    """Test exporting transactions when none exist"""
    response = client.get("/accounts/transactions/export/csv")
    assert response.status_code == 200
    assert "account_id,date,amount,description,category,notes" in response.text


def test_export_transactions_with_data(create_test_account) -> None:
    """Test exporting transactions with data"""
    account_id = create_test_account
    
    txn_data = {
        "account_id": account_id,
        "date": "2024-01-15",
        "amount": 50000.0,
        "description": "Salary",
        "category": "Income",
        "notes": "Monthly salary"
    }
    
    create_response = client.post("/accounts/transactions", json=txn_data)
    assert create_response.status_code == 200
    
    export_response = client.get("/accounts/transactions/export/csv")
    assert export_response.status_code == 200
    
    csv_content = export_response.text
    assert account_id in csv_content
    assert "Salary" in csv_content
    assert "50000" in csv_content
    assert "Income" in csv_content


def test_export_transactions_filtered_by_account(create_test_account) -> None:
    """Test exporting transactions filtered by account"""
    account_id = create_test_account
    
    txn_data = {
        "account_id": account_id,
        "date": "2024-01-15",
        "amount": 50000.0,
        "description": "Salary",
        "category": "Income",
        "notes": None
    }
    client.post("/accounts/transactions", json=txn_data)
    
    export_response = client.get(f"/accounts/transactions/export/csv?account_id={account_id}")
    assert export_response.status_code == 200
    
    csv_content = export_response.text
    assert account_id in csv_content
    assert "Salary" in csv_content


def test_import_transactions_valid_csv(create_test_account) -> None:
    """Test importing valid transactions CSV"""
    account_id = create_test_account
    
    csv_content = f"""account_id,date,amount,description,category,notes
{account_id},2024-01-15,50000,Salary,Income,Monthly salary
{account_id},2024-01-16,-2500,Groceries,Food,Weekly shopping"""
    
    response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 2
    assert len(data["errors"]) == 0
    assert data["total_rows"] == 2


def test_import_transactions_missing_account_id(setup_db) -> None:
    """Test importing transactions with missing account ID"""
    csv_content = """account_id,date,amount,description,category,notes
,2024-01-15,50000,Salary,Income,Test"""
    
    response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Account ID is required" in data["errors"][0]


def test_import_transactions_missing_date(create_test_account) -> None:
    """Test importing transactions with missing date"""
    account_id = create_test_account
    
    csv_content = f"""account_id,date,amount,description,category,notes
{account_id},,50000,Salary,Income,Test"""
    
    response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Date is required" in data["errors"][0]


def test_import_transactions_missing_description(create_test_account) -> None:
    """Test importing transactions with missing description"""
    account_id = create_test_account
    
    csv_content = f"""account_id,date,amount,description,category,notes
{account_id},2024-01-15,50000,,Income,Test"""
    
    response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Description is required" in data["errors"][0]


def test_import_transactions_missing_category(create_test_account) -> None:
    """Test importing transactions with missing category"""
    account_id = create_test_account
    
    csv_content = f"""account_id,date,amount,description,category,notes
{account_id},2024-01-15,50000,Salary,,Test"""
    
    response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0
    assert "Category is required" in data["errors"][0]


def test_import_transactions_invalid_date_format(create_test_account) -> None:
    """Test importing transactions with invalid date format"""
    account_id = create_test_account
    
    csv_content = f"""account_id,date,amount,description,category,notes
{account_id},15/01/2024,50000,Salary,Income,Test"""
    
    response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0


def test_import_transactions_mixed_valid_invalid(create_test_account) -> None:
    """Test importing mix of valid and invalid transactions"""
    account_id = create_test_account
    
    csv_content = f"""account_id,date,amount,description,category,notes
{account_id},2024-01-15,50000,Salary,Income,Valid transaction
{account_id},,25000,Bonus,Income,Invalid - no date
{account_id},2024-01-16,-2500,Groceries,Food,Valid transaction"""
    
    response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 2
    assert len(data["errors"]) == 1
    assert data["total_rows"] == 3


def test_import_transactions_with_positive_and_negative_amounts(create_test_account) -> None:
    """Test importing transactions with both positive and negative amounts"""
    account_id = create_test_account
    
    csv_content = f"""account_id,date,amount,description,category,notes
{account_id},2024-01-15,50000,Salary,Income,Income transaction
{account_id},2024-01-16,-2500,Groceries,Food,Expense transaction
{account_id},2024-01-17,-1000,Transport,Travel,Expense transaction"""
    
    response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 3
    assert len(data["errors"]) == 0


def test_export_import_roundtrip(create_test_account) -> None:
    """Test export then import maintains data integrity"""
    account_id = create_test_account
    
    txn_data = {
        "account_id": account_id,
        "date": "2024-01-15",
        "amount": 50000.0,
        "description": "Test Transaction",
        "category": "Test Category",
        "notes": "Test notes"
    }
    
    client.post("/accounts/transactions", json=txn_data)
    
    export_response = client.get("/accounts/transactions/export/csv")
    csv_content = export_response.text
    
    setup_db = get_connection()
    setup_db.execute("DELETE FROM transactions")
    setup_db.commit()
    setup_db.close()
    
    import_response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert import_response.status_code == 200
    data = import_response.json()
    assert data["created"] == 1
    
    list_response = client.get("/accounts/transactions/")
    transactions = list_response.json()
    assert len(transactions) == 1
    assert transactions[0]["description"] == "Test Transaction"
    assert float(transactions[0]["amount"]) == 50000.0


def test_import_transactions_with_optional_notes(create_test_account) -> None:
    """Test importing transactions with and without notes"""
    account_id = create_test_account
    
    csv_content = f"""account_id,date,amount,description,category,notes
{account_id},2024-01-15,50000,Salary,Income,Has notes
{account_id},2024-01-16,-2500,Groceries,Food,"""
    
    response = client.post(
        "/accounts/transactions/import/csv",
        json={"file_content": csv_content}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 2
    assert len(data["errors"]) == 0


def test_export_transactions_multiple_accounts(setup_db) -> None:
    """Test exporting transactions from multiple accounts"""
    acc1_data = {"name": "Account 1", "type": "BANK", "institution": "Bank 1", "notes": None}
    acc2_data = {"name": "Account 2", "type": "CARD", "institution": "Bank 2", "notes": None}
    
    acc1_response = client.post("/accounts/", json=acc1_data)
    acc2_response = client.post("/accounts/", json=acc2_data)
    
    acc1_id = acc1_response.json()["id"]
    acc2_id = acc2_response.json()["id"]
    
    client.post("/accounts/transactions", json={
        "account_id": acc1_id, "date": "2024-01-15", "amount": 5000.0,
        "description": "Txn 1", "category": "Cat 1", "notes": None
    })
    client.post("/accounts/transactions", json={
        "account_id": acc2_id, "date": "2024-01-16", "amount": -3000.0,
        "description": "Txn 2", "category": "Cat 2", "notes": None
    })
    
    export_response = client.get("/accounts/transactions/export/csv")
    assert export_response.status_code == 200
    
    csv_content = export_response.text
    assert acc1_id in csv_content
    assert acc2_id in csv_content
    assert "Txn 1" in csv_content
    assert "Txn 2" in csv_content

# Made with Bob
