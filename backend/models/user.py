import uuid
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100))
    google_Id = Column(String(255), unique=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    phone = Column(String(20))
    deleted_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # ✅ Add this relationship
    verification_codes = relationship(
        "VerificationCode",
        back_populates="user",
        cascade="all, delete-orphan"
    )