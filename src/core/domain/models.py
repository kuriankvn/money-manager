from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


# User Schemas
class UserSchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str


# Category Schemas
class CategorySchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    user_uid: str


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str
    user_uid: str
    user_name: str


# Transaction Schemas
class TransactionSchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    amount: float = Field(default=..., gt=0)
    date: float
    type: Literal["income", "expense"]
    user_uid: str
    category_uid: str


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str
    amount: float
    date: float
    type: str
    user_uid: str
    user_name: str
    category_uid: str
    category_name: str


# Subscription Schemas
class SubscriptionSchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    amount: float = Field(default=..., gt=0)
    interval: Literal["monthly", "yearly"]
    multiplier: int = Field(default=..., gt=0)
    user_uid: str
    category_uid: str
    active: bool


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str
    amount: float
    interval: str
    multiplier: int
    user_uid: str
    user_name: str
    category_uid: str
    category_name: str
    active: bool

# Made with Bob
