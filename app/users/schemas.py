"""
User domain Pydantic schemas for Supabase Authentication.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_dev: bool = False

    model_config = ConfigDict(from_attributes=True)
