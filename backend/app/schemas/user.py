from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    company_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    company_name: Optional[str]
    logo_path: Optional[str]
    vat_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
