from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


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
