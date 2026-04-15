from pydantic import BaseModel, field_validator
from typing import Optional, List

TIPOS_HORARIO_VALIDOS = ['general', 'split_10', 'split_11', 'split_12']

class GrupoCreate(BaseModel):
    nombre:           str
    nivel:            int
    seccion:          str
    especialidad_ids: List[int] = []
    num_estudiantes:  int = 30
    tipo_horario:     str = 'general'

    @field_validator("nivel")
    def validar_nivel(cls, v):
        if v not in [10, 11, 12]:
            raise ValueError("El nivel debe ser 10, 11 o 12")
        return v

    @field_validator("num_estudiantes")
    def validar_estudiantes(cls, v):
        if not 1 <= v <= 50:
            raise ValueError("El número de estudiantes debe estar entre 1 y 50")
        return v

class GrupoUpdate(BaseModel):
    nombre:           Optional[str]       = None
    num_estudiantes:  Optional[int]       = None
    tipo_horario:     Optional[str]       = None
    especialidad_ids: Optional[List[int]] = None
    activo:           Optional[bool]      = None

class EspecialidadBasica(BaseModel):
    id:     int
    nombre: str
    codigo: str
    class Config: from_attributes = True

class GrupoResponse(BaseModel):
    id:              int
    nombre:          str
    nivel:           int
    seccion:         str
    especialidades:  List[EspecialidadBasica] = []
    num_estudiantes: int
    tipo_horario:    str
    activo:          bool

    class Config: from_attributes = True
