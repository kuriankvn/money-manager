"""API client for Money Manager backend"""
import requests
from typing import Any


BASE_URL = "http://localhost:8000"


def handle_response(response: requests.Response) -> tuple[bool, Any]:
    """Handle API response and return success status and data/error"""
    try:
        if response.status_code in (200, 201):
            return True, response.json()
        elif response.status_code == 204:
            return True, "Operation successful"
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Error {response.status_code}: {error_detail}"
    except Exception as e:
        return False, f"Request failed: {str(e)}"


def get_accounts() -> tuple[bool, Any]:
    """Get all accounts"""
    try:
        response = requests.get(f"{BASE_URL}/accounts")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_transactions(account_id: str | None = None) -> tuple[bool, Any]:
    """Get transactions"""
    try:
        url = f"{BASE_URL}/accounts/transactions/"
        if account_id:
            url = f"{BASE_URL}/accounts/{account_id}/transactions"
        response = requests.get(url)
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_transaction(
    account_id: str,
    date: str,
    amount: float,
    description: str,
    category: str,
    notes: str | None
) -> tuple[bool, Any]:
    """Create a new transaction"""
    try:
        response = requests.post(
            f"{BASE_URL}/accounts/transactions",
            json={
                "account_id": account_id,
                "date": date,
                "amount": amount,
                "description": description,
                "category": category,
                "notes": notes
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def export_transactions_csv(account_id: str | None = None) -> tuple[bool, Any]:
    """Export transactions to CSV"""
    try:
        url = f"{BASE_URL}/accounts/transactions/export/csv"
        if account_id:
            url += f"?account_id={account_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return True, response.text
        else:
            return False, f"Error {response.status_code}: Failed to export"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def import_transactions_csv(csv_content: str) -> tuple[bool, Any]:
    """Import transactions from CSV"""
    try:
        response = requests.post(
            f"{BASE_URL}/accounts/transactions/import/csv",
            json={"file_content": csv_content}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_subscriptions() -> tuple[bool, Any]:
    """Get all subscriptions"""
    try:
        response = requests.get(f"{BASE_URL}/subscriptions")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_active_subscriptions() -> tuple[bool, Any]:
    """Get active subscriptions"""
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/active")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_subscription(
    name: str,
    sub_type: str,
    frequency: str,
    due_day: int,
    expected_amount: float,
    start_date: str,
    end_date: str | None,
    notes: str | None,
    generate_instances: bool
) -> tuple[bool, Any]:
    """Create a new subscription"""
    try:
        response = requests.post(
            f"{BASE_URL}/subscriptions",
            json={
                "name": name,
                "type": sub_type,
                "frequency": frequency,
                "due_day": due_day,
                "expected_amount": expected_amount,
                "start_date": start_date,
                "end_date": end_date,
                "notes": notes,
                "generate_instances": generate_instances
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_due_instances() -> tuple[bool, Any]:
    """Get due subscription instances"""
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/instances/due")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def mark_instance_paid(instance_id: str, paid_date: str, actual_amount: float | None) -> tuple[bool, Any]:
    """Mark subscription instance as paid"""
    try:
        response = requests.post(
            f"{BASE_URL}/subscriptions/instances/{instance_id}/mark-paid",
            json={"paid_date": paid_date, "actual_amount": actual_amount}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def export_subscriptions_csv() -> tuple[bool, Any]:
    """Export subscriptions to CSV"""
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/export/csv")
        if response.status_code == 200:
            return True, response.text
        else:
            return False, f"Error {response.status_code}: Failed to export"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def import_subscriptions_csv(csv_content: str) -> tuple[bool, Any]:
    """Import subscriptions from CSV"""
    try:
        response = requests.post(
            f"{BASE_URL}/subscriptions/import/csv",
            json={"file_content": csv_content}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_investments() -> tuple[bool, Any]:
    """Get all investments"""
    try:
        response = requests.get(f"{BASE_URL}/investments")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_investment(
    name: str,
    provider: str,
    inv_type: str,
    notes: str | None
) -> tuple[bool, Any]:
    """Create a new investment"""
    try:
        response = requests.post(
            f"{BASE_URL}/investments",
            json={
                "name": name,
                "provider": provider,
                "type": inv_type,
                "notes": notes
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def add_contribution(
    investment_id: str,
    date: str,
    amount: float,
    notes: str | None
) -> tuple[bool, Any]:
    """Add investment contribution"""
    try:
        response = requests.post(
            f"{BASE_URL}/investments/contributions",
            json={
                "investment_id": investment_id,
                "date": date,
                "amount": amount,
                "notes": notes
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_contributions(investment_id: str) -> tuple[bool, Any]:
    """Get contributions for an investment"""
    try:
        response = requests.get(f"{BASE_URL}/investments/{investment_id}/contributions")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def add_snapshot(
    investment_id: str,
    date: str,
    current_value: float
) -> tuple[bool, Any]:
    """Add investment value snapshot"""
    try:
        response = requests.post(
            f"{BASE_URL}/investments/snapshots",
            json={
                "investment_id": investment_id,
                "date": date,
                "current_value": current_value
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_investment_summary(investment_id: str) -> tuple[bool, Any]:
    """Get investment summary"""
    try:
        response = requests.get(f"{BASE_URL}/investments/{investment_id}/summary")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_portfolio_summary() -> tuple[bool, Any]:
    """Get portfolio summary"""
    try:
        response = requests.get(f"{BASE_URL}/investments/portfolio/summary")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def export_investments_csv() -> tuple[bool, Any]:
    """Export investments to CSV"""
    try:
        response = requests.get(f"{BASE_URL}/investments/export/csv")
        if response.status_code == 200:
            return True, response.text
        else:
            return False, f"Error {response.status_code}: Failed to export"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def import_investments_csv(csv_content: str) -> tuple[bool, Any]:
    """Import investments from CSV"""
    try:
        response = requests.post(
            f"{BASE_URL}/investments/import/csv",
            json={"file_content": csv_content}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def export_contributions_csv(investment_id: str | None = None) -> tuple[bool, Any]:
    """Export contributions to CSV"""
    try:
        url = f"{BASE_URL}/investments/contributions/export/csv"
        if investment_id:
            url += f"?investment_id={investment_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return True, response.text
        else:
            return False, f"Error {response.status_code}: Failed to export"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def import_contributions_csv(csv_content: str) -> tuple[bool, Any]:
    """Import contributions from CSV"""
    try:
        response = requests.post(
            f"{BASE_URL}/investments/contributions/import/csv",
            json={"file_content": csv_content}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# Made with Bob
