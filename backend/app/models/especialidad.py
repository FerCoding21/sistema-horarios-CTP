from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.grupo import grupo_especialidades


class Especialidad(Base):
    __tablename__ = "especialidades"

    id         = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String(100), nullable=False, unique=True)
    codigo     = Column(String(20),  nullable=False, unique=True)
    activo     = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    grupos = relationship("Grupo", secondary=grupo_especialidades, back_populates="especialidades")