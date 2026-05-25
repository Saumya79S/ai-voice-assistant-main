from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from database import Base


class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    vapi_call_id = Column(String(100), nullable=True, unique=True)
    assistant_name = Column(String(100), nullable=True)
    assistant_phone_number = Column(String(30), nullable=True)
    customer_phone_number = Column(String(30), nullable=True)
    call_type = Column(String(30), nullable=True)       # inboundPhoneCall, webCall, outboundPhoneCall and internation call
    ended_reason = Column(String(100), nullable=True)
    success_evaluation = Column(String(50), nullable=True)
    score = Column(Float, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)  # New field for call cost
    transcript = Column(String(10000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
