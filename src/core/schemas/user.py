from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)


class UserUpdate(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str


# Made with Bob