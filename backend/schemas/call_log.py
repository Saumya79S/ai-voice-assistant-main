from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CallLogOut(BaseModel):
    id: int
    vapi_call_id: Optional[str]
    assistant_name: Optional[str]
    assistant_phone_number: Optional[str]
    customer_phone_number: Optional[str]
    call_type: Optional[str]
    ended_reason: Optional[str]
    success_evaluation: Optional[str]
    score: Optional[float]
    cost: Optional[float]
    start_time: Optional[datetime]
    duration_seconds: Optional[float]
    transcript: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
