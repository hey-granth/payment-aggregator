from pydantic import BaseModel
from typing import Optional
from uuid import UUID


# schema for the JWT token response when a user logs in
class Token(BaseModel):
    access_token: str
    token_type: str


# payload of the JWT token
class TokenData(BaseModel):
    username: Optional[str] = None


# contains common fields for UserCreate and User
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    username: str


# request schema while creating a new user
class UserCreate(UserBase):
    password: str


# response schema while creating a new user
class User(UserBase):
    id: UUID
    is_active: bool

    class Config:
        from_attributes = True
        # we use from_attributes only in the case when we need to create pydantic models using database objects directly, instead of dicts
