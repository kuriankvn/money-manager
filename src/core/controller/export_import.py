from fastapi import APIRouter, status, Body, Response
from typing import Any
from core.services import TransactionService, SubscriptionService

# Initialize services
transaction_service = TransactionService()
subscription_service = SubscriptionService()

# Create routers
transactions_export_router = APIRouter(prefix="/transactions/export", tags=["transactions-export"])
subscriptions_export_router = APIRouter(prefix="/subscriptions/export", tags=["subscriptions-export"])


# Transaction Export/Import Routes
@transactions_export_router.get("/csv", response_class=Response)
def export_transactions_csv() -> Response:
    """Export all transactions to CSV"""
    csv_content: str = transaction_service.export_to_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )


@transactions_export_router.post("/csv", status_code=status.HTTP_201_CREATED)
def import_transactions_csv(file_content: str = Body(..., embed=True)) -> dict[str, Any]:
    """Import transactions from CSV"""
    return transaction_service.import_from_csv(csv_content=file_content)


# Subscription Export/Import Routes
@subscriptions_export_router.get("/csv", response_class=Response)
def export_subscriptions_csv() -> Response:
    """Export all subscriptions to CSV"""
    csv_content: str = subscription_service.export_to_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=subscriptions.csv"}
    )


@subscriptions_export_router.post("/csv", status_code=status.HTTP_201_CREATED)
def import_subscriptions_csv(file_content: str = Body(..., embed=True)) -> dict[str, Any]:
    """Import subscriptions from CSV"""
    return subscription_service.import_from_csv(csv_content=file_content)

# Made with Bob