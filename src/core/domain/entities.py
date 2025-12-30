from datetime import date
from typing import Optional
from dataclasses import dataclass

from .base import (
    Frequency,
    SubscriptionStatus,
    SubscriptionInstanceStatus,
    InvestmentStatus,
    InvestmentPlanStatus,
    InvestmentPlanInstanceStatus,
)


@dataclass
class Category:
    uid: str
    name: str


@dataclass
class Account:
    uid: str
    name: str


@dataclass
class Transaction:
    uid: str
    name: str
    amount: float
    date: date
    account_id: str
    category_id: str


@dataclass
class Subscription:
    uid: str
    name: str
    amount: float
    frequency: Frequency
    interval: int
    status: SubscriptionStatus


@dataclass
class SubscriptionInstance:
    uid: str
    subscription_id: str
    amount: float
    due_date: date
    transaction_id: Optional[str]
    status: SubscriptionInstanceStatus


@dataclass
class Investment:
    uid: str
    name: str
    start_date: date
    status: InvestmentStatus


@dataclass
class InvestmentValueSnapshot:
    uid: str
    investment_id: str
    date: date
    current_value: float


@dataclass
class InvestmentPlan:
    uid: str
    investment_id: str
    amount: float
    frequency: Frequency
    interval: int
    status: InvestmentPlanStatus


@dataclass
class InvestmentPlanInstance:
    uid: str
    investment_plan_id: str
    amount: float
    due_date: date
    transaction_id: Optional[str]
    status: InvestmentPlanInstanceStatus
