from sqlalchemy import Column, Integer, Time, Boolean, SmallInteger
from database import Base


class AvailabilityRule(Base):
    __tablename__ = "availability_rules"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(SmallInteger, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration = Column(Integer, default=30)  # minutes
    is_active = Column(Boolean, default=True)
