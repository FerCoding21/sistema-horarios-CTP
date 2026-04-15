from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Tabla de asociación M2M entre grupos y especialidades
grupo_especialidades = Table(
    'grupo_especialidades',
    Base.metadata,
    Column('grupo_id',        Integer, ForeignKey('grupos.id'),        primary_key=True),
    Column('especialidad_id', Integer, ForeignKey('especialidades.id'), primary_key=True),
)


class Grupo(Base):
    __tablename__ = "grupos"

    id              = Column(Integer,    primary_key=True, index=True)
    nombre          = Column(String(20), nullable=False, unique=True)
    nivel           = Column(Integer,    nullable=False)
    seccion         = Column(String(5),  nullable=False)
    num_estudiantes = Column(Integer,    nullable=False, default=30)
    # 'general'   → grupos 5-10 de cada nivel (una sola especialidad, sin restricción de días)
    # 'split_10'  → técnicas Lun+Mar+Mié-AM, académicas Mié-PM+Jue+Vie
    # 'split_11'  → técnicas Lun+Mar, académicas Mié+Jue+Vie
    # 'split_12'  → técnicas Lun+Mar, académicas Mié+Jue+Vie
    tipo_horario    = Column(String(20), nullable=False, default='general')
    activo          = Column(Boolean,    nullable=False, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    especialidades = relationship("Especialidad", secondary=grupo_especialidades,
                                  back_populates="grupos")
    lecciones      = relationship("Horario", back_populates="grupo")
