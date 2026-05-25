from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AgentCreate(BaseModel):
    name: str = Field(default="AI Receptionist", min_length=1, max_length=100)
    prompt: str = Field(..., min_length=1, max_length=10000)
    voice: str = Field(default="nova", min_length=1, max_length=100)
    is_active: bool = True

    @field_validator("name", "prompt", "voice")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("value cannot be blank")
        return normalized


class AgentOut(BaseModel):
    id: int
    name: str
    prompt: str
    voice: str
    vapi_assistant_id: Optional[str]
    is_active: bool
    created_at: datetime
    # Set by API routes when Vapi sync fails (not a DB column).
    vapi_sync_error: Optional[str] = None

    class Config:
        from_attributes = True


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    voice: Optional[str] = None
    is_active: Optional[bool] = None
    vapi_assistant_id: Optional[str] = None

    @field_validator("name", "prompt", "voice")
    @classmethod
    def validate_optional_non_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("value cannot be blank")
        return normalized
