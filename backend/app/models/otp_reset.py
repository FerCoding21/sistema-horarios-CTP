from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class OtpReset(Base):
    __tablename__ = "otp_reset"

    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String(150), nullable=False, index=True)
    otp_hash   = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    usado      = Column(Boolean, default=False, nullable=False)
