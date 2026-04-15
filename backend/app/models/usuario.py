from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id            = Column(Integer,     primary_key=True, index=True)
    nombre        = Column(String(100), nullable=False)
    email         = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    rol           = Column(String(20),  nullable=False)
    activo        = Column(Boolean,     nullable=False, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
