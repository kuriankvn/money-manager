from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status, Query
from core.repositories import PaymentRepository
from core.models import Payment
from core.schemas import (
    PaymentResponse,
    GeneratePaymentsRequest,
    MarkPaidRequest
)
from core.services import PaymentService

router: APIRouter = APIRouter(prefix="/payments", tags=["payments"])
payment_repo: PaymentRepository = PaymentRepository()
payment_service: PaymentService = PaymentService()


@router.post(path="/generate", status_code=status.HTTP_201_CREATED)
def generate_payments(request: GeneratePaymentsRequest) -> dict[str, Any]:
    """Generate payment notifications for all active subscriptions for a given month"""
    result = payment_service.generate_payments_for_month(
        month=request.month,
        year=request.year,
        user_uid=request.user_uid
    )
    return result


@router.get(path="/{uid}", response_model=PaymentResponse)
def get_payment(uid: str) -> PaymentResponse:
    """Get payment by ID"""
    payment: Optional[Payment] = payment_repo.get_by_id(uid=uid)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    return PaymentResponse(
        uid=payment.uid,
        amount=payment.amount,
        due_date=payment.due_date,
        user_uid=payment.user.uid,
        user_name=payment.user.name,
        subscription_uid=payment.subscription.uid,
        subscription_name=payment.subscription.name,
        paid_date=payment.paid_date,
        paid=payment.paid
    )


@router.get(path="/", response_model=list[PaymentResponse])
def get_payments(
    month: Optional[int] = Query(default=None, ge=1, le=12),
    year: Optional[int] = Query(default=None, ge=2000),
    user_uid: Optional[str] = Query(default=None)
) -> list[PaymentResponse]:
    """Get all payments, optionally filtered by month/year and user"""
    if month and year:
        payments: list[Payment] = payment_service.get_payments_by_month(
            month=month,
            year=year,
            user_uid=user_uid
        )
    else:
        payments = payment_repo.get_all()
        if user_uid:
            payments = [p for p in payments if p.user.uid == user_uid]
    
    return [
        PaymentResponse(
            uid=payment.uid,
            amount=payment.amount,
            due_date=payment.due_date,
            user_uid=payment.user.uid,
            user_name=payment.user.name,
            subscription_uid=payment.subscription.uid,
            subscription_name=payment.subscription.name,
            paid_date=payment.paid_date,
            paid=payment.paid
        )
        for payment in payments
    ]


@router.put(path="/{uid}/mark-paid", response_model=PaymentResponse)
def mark_payment_as_paid(uid: str, request: MarkPaidRequest) -> PaymentResponse:
    """Mark a payment as paid"""
    success: bool = payment_service.mark_as_paid(
        payment_uid=uid,
        paid_date=request.paid_date
    )
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    payment: Optional[Payment] = payment_repo.get_by_id(uid=uid)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    return PaymentResponse(
        uid=payment.uid,
        amount=payment.amount,
        due_date=payment.due_date,
        user_uid=payment.user.uid,
        user_name=payment.user.name,
        subscription_uid=payment.subscription.uid,
        subscription_name=payment.subscription.name,
        paid_date=payment.paid_date,
        paid=payment.paid
    )


@router.get(path="/statistics/{month}/{year}")
def get_payment_statistics(
    month: int,
    year: int,
    user_uid: Optional[str] = Query(default=None)
) -> dict[str, float | int]:
    """Get payment statistics for a given month"""
    return payment_service.get_payment_statistics(
        month=month,
        year=year,
        user_uid=user_uid
    )


@router.delete(path="/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(uid: str) -> None:
    """Delete payment"""
    success: bool = payment_repo.delete(uid=uid)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

# Made with Bob
