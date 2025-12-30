"""Pydantic schemas for API requests and responses."""
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from app.accounts.models import AccountType
from app.subscriptions.models import SubscriptionType, Frequency, InstanceStatus
from app.investments.models import InvestmentType


class AccountCreate(BaseModel):
    name: str
    type: AccountType
    institution: str
    notes: Optional[str] = None


class AccountResponse(BaseModel):
    id: str
    name: str
    type: AccountType
    institution: str
    notes: Optional[str] = None


class TransactionCreate(BaseModel):
    account_id: str
    date: date
    amount: Decimal
    description: str
    category: str
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    account_id: str
    date: date
    amount: Decimal
    description: str
    category: str
    notes: Optional[str] = None


class SubscriptionCreate(BaseModel):
    name: str
    type: SubscriptionType
    frequency: Frequency
    due_day: int = Field(ge=1, le=31)
    expected_amount: Decimal
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None
    generate_instances: bool = True


class SubscriptionResponse(BaseModel):
    id: str
    name: str
    type: SubscriptionType
    frequency: Frequency
    due_day: int
    expected_amount: Decimal
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None


class SubscriptionInstanceResponse(BaseModel):
    id: str
    subscription_id: str
    period: str
    due_date: date
    amount: Decimal
    status: InstanceStatus
    paid_date: Optional[date] = None


class MarkInstancePaid(BaseModel):
    paid_date: date
    actual_amount: Optional[Decimal] = None


class InvestmentCreate(BaseModel):
    name: str
    provider: str
    type: InvestmentType
    notes: Optional[str] = None


class InvestmentResponse(BaseModel):
    id: str
    name: str
    provider: str
    type: InvestmentType
    notes: Optional[str] = None


class ContributionCreate(BaseModel):
    investment_id: str
    date: date
    amount: Decimal
    notes: Optional[str] = None


class ContributionResponse(BaseModel):
    id: str
    investment_id: str
    date: date
    amount: Decimal
    notes: Optional[str] = None


class SnapshotCreate(BaseModel):
    investment_id: str
    date: date
    current_value: Decimal


class SnapshotResponse(BaseModel):
    id: str
    investment_id: str
    date: date
    current_value: Decimal

# Made with Bob
