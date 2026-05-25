from pydantic import BaseModel, Field, model_validator
from datetime import time
from typing import Optional


class AvailabilityRuleCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    slot_duration: int = Field(default=30, ge=5, le=480)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class AvailabilityRuleOut(BaseModel):
    id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration: int
    is_active: bool

    class Config:
        from_attributes = True


class AvailabilityRuleUpdate(BaseModel):
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_duration: Optional[int] = Field(default=None, ge=5, le=480)
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_partial_update(self):
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            raise ValueError("start_time must be before end_time")
        return self


class SlotOut(BaseModel):
    date: str
    start_time: str
    end_time: str
    available: bool
