from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    user_uid: str


class CategoryUpdate(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)
    user_uid: str


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str
    user_uid: str
    user_name: str


# Made with Bob