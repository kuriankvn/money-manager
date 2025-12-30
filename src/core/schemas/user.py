from pydantic import BaseModel, Field, ConfigDict


class UserSchema(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    name: str
