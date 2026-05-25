from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    date: date
    start_time: time
    notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("name cannot be blank")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        phone = value.strip()
        allowed = set("+0123456789 -()")
        if any(char not in allowed for char in phone):
            raise ValueError("phone contains invalid characters")
        digits_count = sum(char.isdigit() for char in phone)
        if digits_count < 7:
            raise ValueError("phone must contain at least 7 digits")
        return phone

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        notes = value.strip()
        return notes or None


class AppointmentOut(BaseModel):
    id: int
    name: str
    phone: str
    date: date
    start_time: time
    end_time: time
    status: AppointmentStatus
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("notes")
    @classmethod
    def validate_update_notes(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        notes = value.strip()
        return notes or None
