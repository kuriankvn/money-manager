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
    datetime: float,
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
                "datetime": datetime,
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
    datetime: float,
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
                "datetime": datetime,
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


# Made with Bob