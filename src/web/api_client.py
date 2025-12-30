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


# Users API
def get_users() -> tuple[bool, Any]:
    """Get all users"""
    try:
        response = requests.get(f"{BASE_URL}/users")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def create_user(name: str) -> tuple[bool, Any]:
    """Create a new user"""
    try:
        response = requests.post(f"{BASE_URL}/users", json={"name": name})
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_user(uid: str, name: str) -> tuple[bool, Any]:
    """Update a user"""
    try:
        response = requests.put(f"{BASE_URL}/users/{uid}", json={"name": name})
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_user(uid: str) -> tuple[bool, Any]:
    """Delete a user"""
    try:
        response = requests.delete(f"{BASE_URL}/users/{uid}")
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


def create_category(name: str, user_uid: str) -> tuple[bool, Any]:
    """Create a new category"""
    try:
        response = requests.post(
            f"{BASE_URL}/categories",
            json={"name": name, "user_uid": user_uid}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_category(uid: str, name: str, user_uid: str) -> tuple[bool, Any]:
    """Update a category"""
    try:
        response = requests.put(
            f"{BASE_URL}/categories/{uid}",
            json={"name": name, "user_uid": user_uid}
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
    date: float,
    type: str,
    user_uid: str,
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
                "type": type,
                "user_uid": user_uid,
                "category_uid": category_uid
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_transaction(
    uid: str,
    name: str,
    amount: float,
    date: float,
    type: str,
    user_uid: str,
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
                "type": type,
                "user_uid": user_uid,
                "category_uid": category_uid
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
    interval: str,
    multiplier: int,
    user_uid: str,
    category_uid: str,
    active: bool
) -> tuple[bool, Any]:
    """Create a new subscription"""
    try:
        response = requests.post(
            f"{BASE_URL}/subscriptions",
            json={
                "name": name,
                "amount": amount,
                "interval": interval,
                "multiplier": multiplier,
                "user_uid": user_uid,
                "category_uid": category_uid,
                "active": active
            }
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def update_subscription(
    uid: str,
    name: str,
    amount: float,
    interval: str,
    multiplier: int,
    user_uid: str,
    category_uid: str,
    active: bool
) -> tuple[bool, Any]:
    """Update a subscription"""
    try:
        response = requests.put(
            f"{BASE_URL}/subscriptions/{uid}",
            json={
                "name": name,
                "amount": amount,
                "interval": interval,
                "multiplier": multiplier,
                "user_uid": user_uid,
                "category_uid": category_uid,
                "active": active
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
            f"{BASE_URL}/subscriptions/import/csv",
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
            f"{BASE_URL}/transactions/import/csv",
            json={"file_content": csv_content}
        )
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


# Subscription Payments API
def generate_payments(month: int, year: int, user_uid: str | None = None) -> tuple[bool, Any]:
    """Generate payment notifications for a given month"""
    try:
        payload: dict[str, Any] = {"month": month, "year": year}
        if user_uid:
            payload["user_uid"] = user_uid
        response = requests.post(f"{BASE_URL}/payments/generate", json=payload)
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_payments(month: int | None = None, year: int | None = None, user_uid: str | None = None) -> tuple[bool, Any]:
    """Get subscription payments, optionally filtered by month/year and user"""
    try:
        params: dict[str, Any] = {}
        if month:
            params["month"] = month
        if year:
            params["year"] = year
        if user_uid:
            params["user_uid"] = user_uid
        response = requests.get(f"{BASE_URL}/payments", params=params)
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_payment(uid: str) -> tuple[bool, Any]:
    """Get a single subscription payment by ID"""
    try:
        response = requests.get(f"{BASE_URL}/payments/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def mark_payment_as_paid(uid: str, paid_date: str | None = None) -> tuple[bool, Any]:
    """Mark a payment as paid"""
    try:
        payload: dict[str, Any] = {}
        if paid_date:
            payload["paid_date"] = paid_date
        response = requests.put(f"{BASE_URL}/payments/{uid}/mark-paid", json=payload)
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_payment_statistics(month: int, year: int, user_uid: str | None = None) -> tuple[bool, Any]:
    """Get payment statistics for a given month"""
    try:
        params: dict[str, Any] = {}
        if user_uid:
            params["user_uid"] = user_uid
        response = requests.get(f"{BASE_URL}/payments/statistics/{month}/{year}", params=params)
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def delete_payment(uid: str) -> tuple[bool, Any]:
    """Delete a subscription payment"""
    try:
        response = requests.delete(f"{BASE_URL}/payments/{uid}")
        return handle_response(response)
    except Exception as e:
        return False, f"Connection error: {str(e)}"
        return False, f"Connection error: {str(e)}"
