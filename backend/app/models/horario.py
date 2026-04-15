from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Horario(Base):
    __tablename__ = "horario"
    __table_args__ = (
        # En el modelo de pistas paralelas, dos materias de distinta especialidad
        # pueden compartir el mismo slot para el mismo grupo (son 15+15 alumnos en
        # aulas diferentes). La unicidad se garantiza a nivel de aplicación.
        UniqueConstraint("grupo_id", "materia_id", "dia", "leccion_inicio", "anno_lectivo",
                         name="horario_grupo_materia_slot_unique"),
    )

    id             = Column(Integer, primary_key=True, index=True)
    grupo_id       = Column(Integer, ForeignKey("grupos.id"),   nullable=False)
    materia_id     = Column(Integer, ForeignKey("materias.id"), nullable=False)
    dia            = Column(String(15), nullable=False)
    bloque         = Column(Integer,    nullable=False)
    leccion_inicio = Column(Integer,    nullable=False, default=1)
    leccion_fin    = Column(Integer,    nullable=False, default=1)
    anno_lectivo   = Column(Integer,    nullable=False)
    es_manual      = Column(Boolean,    nullable=False, default=False)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    grupo   = relationship("Grupo",   back_populates="lecciones")
    materia = relationship("Materia", back_populates="lecciones")
