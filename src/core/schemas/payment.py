from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class PaymentSchema(BaseModel):
    amount: float = Field(default=..., gt=0)
    due_date: datetime
    user_uid: str
    subscription_uid: str
    paid_date: Optional[datetime] = None
    paid: bool = False


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    amount: float
    due_date: datetime
    user_uid: str
    user_name: str
    subscription_uid: str
    subscription_name: str
    paid_date: Optional[datetime]
    paid: bool


class GeneratePaymentsRequest(BaseModel):
    month: int = Field(default=..., ge=1, le=12)
    year: int = Field(default=..., ge=2000)
    user_uid: Optional[str] = None


class MarkPaidRequest(BaseModel):
    paid_date: Optional[datetime] = None

# Made with Bob
