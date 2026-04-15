from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Materia(Base):
    __tablename__ = "materias"

    id                  = Column(Integer,     primary_key=True, index=True)
    nombre              = Column(String(100), nullable=False)
    codigo              = Column(String(20),  nullable=False, unique=True)
    tipo                = Column(String(20),  nullable=False)          # academica | tecnica
    lecciones_semanales = Column(Integer,     nullable=False)
    requiere_espacio    = Column(String(30),  nullable=False, default="aula_regular")
    bloques_por_sesion  = Column(Integer,     nullable=False, default=3)
    es_tecnica          = Column(Boolean,     nullable=False, default=False)
    # Niveles en que se imparte: [10], [11], [12], [10,11], [10,11,12], etc.
    niveles_aplicables  = Column(PG_ARRAY(Integer), nullable=False, server_default='{10,11,12}')
    # Especialidad a la que pertenece (NULL = materia académica, compartida por todos)
    especialidad_id     = Column(Integer, ForeignKey("especialidades.id"), nullable=True)
    activo              = Column(Boolean,     nullable=False, default=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    especialidad = relationship("Especialidad")

    dias_permitidos = relationship("MateriaDiaPermitido",
                                    back_populates="materia",
                                    cascade="all, delete-orphan")
    lecciones = relationship("Horario", back_populates="materia")


class MateriaDiaPermitido(Base):
    __tablename__ = "materia_dias_permitidos"

    id         = Column(Integer, primary_key=True, index=True)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False)
    dia        = Column(String(15), nullable=False)

    materia = relationship("Materia", back_populates="dias_permitidos")
