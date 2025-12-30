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


# Accounts API
def get_accounts() -> tuple[bool, Any]:
    """Get all accounts"""
    try:
        response = requests.get(f"{BASE_URL}/accounts")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_account(name: str) -> tuple[bool, Any]:
    """Create a new account"""
    try:
        response = requests.post(f"{BASE_URL}/accounts", json={"name": name})
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_account(uid: str, name: str) -> tuple[bool, Any]:
    """Update an account"""
    try:
        response = requests.put(f"{BASE_URL}/accounts/{uid}", json={"name": name})
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_account(uid: str) -> tuple[bool, Any]:
    """Delete an account"""
    try:
        response = requests.delete(f"{BASE_URL}/accounts/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# Categories API
def get_categories() -> tuple[bool, Any]:
    """Get all categories"""
    try:
        response = requests.get(f"{BASE_URL}/categories")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_category(name: str) -> tuple[bool, Any]:
    """Create a new category"""
    try:
        response = requests.post(
            f"{BASE_URL}/categories",
            json={"name": name}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_category(uid: str, name: str) -> tuple[bool, Any]:
    """Update a category"""
    try:
        response = requests.put(
            f"{BASE_URL}/categories/{uid}",
            json={"name": name}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_category(uid: str) -> tuple[bool, Any]:
    """Delete a category"""
    try:
        response = requests.delete(f"{BASE_URL}/categories/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# Transactions API
def get_transactions() -> tuple[bool, Any]:
    """Get all transactions"""
    try:
        response = requests.get(f"{BASE_URL}/transactions")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_transaction(
    name: str,
    amount: float,
    date: str,
    account_uid: str,
    category_uid: str
) -> tuple[bool, Any]:
    """Create a new transaction"""
    try:
        response = requests.post(
            f"{BASE_URL}/transactions",
            json={
                "name": name,
                "amount": amount,
                "date": date,
                "account_id": account_uid,
                "category_id": category_uid
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_transaction(
    uid: str,
    name: str,
    amount: float,
    date: str,
    account_uid: str,
    category_uid: str
) -> tuple[bool, Any]:
    """Update a transaction"""
    try:
        response = requests.put(
            f"{BASE_URL}/transactions/{uid}",
            json={
                "name": name,
                "amount": amount,
                "date": date,
                "account_id": account_uid,
                "category_id": category_uid
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_transaction(uid: str) -> tuple[bool, Any]:
    """Delete a transaction"""
    try:
        response = requests.delete(f"{BASE_URL}/transactions/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# Subscriptions API
def get_subscriptions() -> tuple[bool, Any]:
    """Get all subscriptions"""
    try:
        response = requests.get(f"{BASE_URL}/subscriptions")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_subscription(
    name: str,
    amount: float,
    frequency: str,
    interval: int,
    status: str
) -> tuple[bool, Any]:
    """Create a new subscription"""
    try:
        response = requests.post(
            f"{BASE_URL}/subscriptions",
            json={
                "name": name,
                "amount": amount,
                "frequency": frequency,
                "interval": interval,
                "status": status
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_subscription(
    uid: str,
    name: str,
    amount: float,
    frequency: str,
    interval: int,
    status: str
) -> tuple[bool, Any]:
    """Update a subscription"""
    try:
        response = requests.put(
            f"{BASE_URL}/subscriptions/{uid}",
            json={
                "name": name,
                "amount": amount,
                "frequency": frequency,
                "interval": interval,
                "status": status
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_subscription(uid: str) -> tuple[bool, Any]:
    """Delete a subscription"""
    try:
        response = requests.delete(f"{BASE_URL}/subscriptions/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"



# Subscription Instances API
def get_subscription_instances() -> tuple[bool, Any]:
    """Get all subscription instances"""
    try:
        response = requests.get(f"{BASE_URL}/subscription-instances")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_subscription_instance(
    subscription_uid: str,
    amount: float,
    due_date: str,
    transaction_uid: str | None = None,
    status: str = "due"
) -> tuple[bool, Any]:
    """Create a new subscription instance"""
    try:
        payload = {
            "subscription_uid": subscription_uid,
            "amount": amount,
            "due_date": due_date,
            "status": status
        }
        if transaction_uid:
            payload["transaction_uid"] = transaction_uid
        response = requests.post(f"{BASE_URL}/subscription-instances", json=payload)
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_subscription_instance(
    uid: str,
    subscription_uid: str,
    amount: float,
    due_date: str,
    transaction_uid: str | None = None,
    status: str = "due"
) -> tuple[bool, Any]:
    """Update a subscription instance"""
    try:
        payload = {
            "subscription_uid": subscription_uid,
            "amount": amount,
            "due_date": due_date,
            "status": status
        }
        if transaction_uid:
            payload["transaction_uid"] = transaction_uid
        response = requests.put(f"{BASE_URL}/subscription-instances/{uid}", json=payload)
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_subscription_instance(uid: str) -> tuple[bool, Any]:
    """Delete a subscription instance"""
    try:
        response = requests.delete(f"{BASE_URL}/subscription-instances/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# Investments API
def get_investments() -> tuple[bool, Any]:
    """Get all investments"""
    try:
        response = requests.get(f"{BASE_URL}/investments")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_investment(name: str, start_date: str, status: str = "active") -> tuple[bool, Any]:
    """Create a new investment"""
    try:
        response = requests.post(
            f"{BASE_URL}/investments",
            json={"name": name, "start_date": start_date, "status": status}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_investment(uid: str, name: str, start_date: str, status: str) -> tuple[bool, Any]:
    """Update an investment"""
    try:
        response = requests.put(
            f"{BASE_URL}/investments/{uid}",
            json={"name": name, "start_date": start_date, "status": status}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_investment(uid: str) -> tuple[bool, Any]:
    """Delete an investment"""
    try:
        response = requests.delete(f"{BASE_URL}/investments/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# Investment Value Snapshots API
def get_investment_snapshots() -> tuple[bool, Any]:
    """Get all investment snapshots"""
    try:
        response = requests.get(f"{BASE_URL}/investment-snapshots")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_investment_snapshot(
    investment_uid: str,
    date: str,
    current_value: float
) -> tuple[bool, Any]:
    """Create a new investment snapshot"""
    try:
        response = requests.post(
            f"{BASE_URL}/investment-snapshots",
            json={
                "investment_uid": investment_uid,
                "date": date,
                "current_value": current_value
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_investment_snapshot(
    uid: str,
    investment_uid: str,
    date: str,
    current_value: float
) -> tuple[bool, Any]:
    """Update an investment snapshot"""
    try:
        response = requests.put(
            f"{BASE_URL}/investment-snapshots/{uid}",
            json={
                "investment_uid": investment_uid,
                "date": date,
                "current_value": current_value
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_investment_snapshot(uid: str) -> tuple[bool, Any]:
    """Delete an investment snapshot"""
    try:
        response = requests.delete(f"{BASE_URL}/investment-snapshots/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# Investment Plans API
def get_investment_plans() -> tuple[bool, Any]:
    """Get all investment plans"""
    try:
        response = requests.get(f"{BASE_URL}/investment-plans")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_investment_plan(
    investment_uid: str,
    amount: float,
    frequency: str,
    interval: int,
    status: str = "active"
) -> tuple[bool, Any]:
    """Create a new investment plan"""
    try:
        response = requests.post(
            f"{BASE_URL}/investment-plans",
            json={
                "investment_uid": investment_uid,
                "amount": amount,
                "frequency": frequency,
                "interval": interval,
                "status": status
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_investment_plan(
    uid: str,
    investment_uid: str,
    amount: float,
    frequency: str,
    interval: int,
    status: str
) -> tuple[bool, Any]:
    """Update an investment plan"""
    try:
        response = requests.put(
            f"{BASE_URL}/investment-plans/{uid}",
            json={
                "investment_uid": investment_uid,
                "amount": amount,
                "frequency": frequency,
                "interval": interval,
                "status": status
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_investment_plan(uid: str) -> tuple[bool, Any]:
    """Delete an investment plan"""
    try:
        response = requests.delete(f"{BASE_URL}/investment-plans/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# Investment Plan Instances API
def get_investment_plan_instances() -> tuple[bool, Any]:
    """Get all investment plan instances"""
    try:
        response = requests.get(f"{BASE_URL}/investment-plan-instances")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_investment_plan_instance(
    investment_plan_uid: str,
    amount: float,
    due_date: str,
    transaction_uid: str | None = None,
    status: str = "planned"
) -> tuple[bool, Any]:
    """Create a new investment plan instance"""
    try:
        payload = {
            "investment_plan_uid": investment_plan_uid,
            "amount": amount,
            "due_date": due_date,
            "status": status
        }
        if transaction_uid:
            payload["transaction_uid"] = transaction_uid
        response = requests.post(f"{BASE_URL}/investment-plan-instances", json=payload)
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_investment_plan_instance(
    uid: str,
    investment_plan_uid: str,
    amount: float,
    due_date: str,
    transaction_uid: str | None = None,
    status: str = "planned"
) -> tuple[bool, Any]:
    """Update an investment plan instance"""
    try:
        payload = {
            "investment_plan_uid": investment_plan_uid,
            "amount": amount,
            "due_date": due_date,
            "status": status
        }
        if transaction_uid:
            payload["transaction_uid"] = transaction_uid
        response = requests.put(f"{BASE_URL}/investment-plan-instances/{uid}", json=payload)
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_investment_plan_instance(uid: str) -> tuple[bool, Any]:
    """Delete an investment plan instance"""
    try:
        response = requests.delete(f"{BASE_URL}/investment-plan-instances/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# CSV Export/Import for Subscriptions
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
            f"{BASE_URL}/subscriptions/export/csv",
            json={"file_content": csv_content}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# CSV Export/Import for Transactions
def export_transactions_csv() -> tuple[bool, Any]:
    """Export transactions to CSV"""
    try:
        response = requests.get(f"{BASE_URL}/transactions/export/csv")
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
            f"{BASE_URL}/transactions/export/csv",
            json={"file_content": csv_content}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


