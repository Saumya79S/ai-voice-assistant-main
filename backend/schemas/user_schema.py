from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone_number: Optional[str] = Field(default=None, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        password = value.strip()
        if not password:
            raise ValueError("password cannot be blank")
        return password

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        phone_number = value.strip()
        if not phone_number:
            return None
        allowed = set("+0123456789 -()")
        if any(char not in allowed for char in phone_number):
            raise ValueError("phone_number contains invalid characters")
        digits_count = sum(char.isdigit() for char in phone_number)
        if digits_count < 7:
            raise ValueError("phone_number must contain at least 7 digits")
        return phone_number


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_login_password(cls, value: str) -> str:
        password = value.strip()
        if not password:
            raise ValueError("password cannot be blank")
        return password


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None
    email: str | None = None


class UserRegistrationResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8)

    @field_validator("token", "new_password")
    @classmethod
    def validate_non_blank_values(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("value cannot be blank")
        return normalized

