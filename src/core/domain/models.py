from datetime import date
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator

from .base import (
    Frequency,
    SubscriptionStatus,
    SubscriptionInstanceStatus,
    InvestmentStatus,
    InvestmentPlanStatus,
    InvestmentPlanInstanceStatus,
)


# Category Schemas
class CategorySchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str


# Account Schemas
class AccountSchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str


# Transaction Schemas
class TransactionSchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    amount: float = Field(default=..., gt=0)
    date: date
    account_id: str
    category_id: str


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str
    amount: float
    date: date
    account_id: str
    category_id: str


# Subscription Schemas
class SubscriptionSchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    amount: float = Field(default=..., gt=0)
    frequency: Frequency
    interval: int = Field(default=..., gt=0)
    due_day: int = Field(default=..., gt=0, lt=32)
    due_month: Optional[int] = Field(default=None, gt=0, lt=13)
    status: SubscriptionStatus

    @model_validator(mode="after")
    def validate_due_month(cls, values) -> Any:
        freq: str = values.frequency
        due_month: Optional[int] = values.due_month
        if freq == "monthly" and due_month is not None:
            raise ValueError("due_month must be null for monthly subscriptions")
        if freq == "yearly" and due_month is None:
            raise ValueError("due_month is required for yearly subscriptions")
        return values


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str
    amount: float
    frequency: Frequency
    interval: int
    due_day: int
    due_month: Optional[int]
    status: SubscriptionStatus


class SubscriptionInstanceSchema(BaseModel):
    subscription_id: str
    amount: float = Field(default=..., gt=0)
    due_date: date
    transaction_id: Optional[str] = None
    status: SubscriptionInstanceStatus


class SubscriptionInstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    subscription_id: str
    amount: float
    due_date: date
    transaction_id: Optional[str] = None
    status: SubscriptionInstanceStatus


# Investment Schemas
class InvestmentSchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    start_date: date
    status: InvestmentStatus


class InvestmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str
    start_date: date
    status: InvestmentStatus


class InvestmentValueSnapshotSchema(BaseModel):
    investment_id: str
    date: date
    current_value: float = Field(default=..., gt=0)


class InvestmentValueSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    investment_id: str
    date: date
    current_value: float


class InvestmentPlanSchema(BaseModel):
    investment_id: str
    amount: float = Field(default=..., gt=0)
    frequency: Frequency
    interval: int = Field(default=..., gt=0)
    status: InvestmentPlanStatus


class InvestmentPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    investment_id: str
    amount: float
    frequency: Frequency
    interval: int
    status: InvestmentPlanStatus


class InvestmentPlanInstanceSchema(BaseModel):
    investment_plan_id: str
    amount: float = Field(default=..., gt=0)
    due_date: date
    transaction_id: Optional[str] = None
    status: InvestmentPlanInstanceStatus


class InvestmentPlanInstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    investment_plan_id: str
    amount: float
    due_date: date
    transaction_id: Optional[str]
    status: InvestmentPlanInstanceStatus

# Made with Bob
