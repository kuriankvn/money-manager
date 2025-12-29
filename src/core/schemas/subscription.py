from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class SubscriptionCreate(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    amount: float = Field(default=..., gt=0)
    interval: Literal["daily", "weekly", "monthly", "yearly"]
    multiplier: int = Field(default=..., gt=0)
    user_uid: str
    category_uid: str
    active: bool = True


class SubscriptionUpdate(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    amount: float = Field(default=..., gt=0)
    interval: Literal["daily", "weekly", "monthly", "yearly"]
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
