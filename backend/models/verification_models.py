# models/verification_models.py
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer



class VerificationCode(Base):
    __tablename__ = 'verification_code'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False, unique=True)
    expiration = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="verification_codes")