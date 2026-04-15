from pydantic import BaseModel, field_validator
from typing import Optional, List

TIPOS_VALIDOS    = ["academica", "tecnica"]
ESPACIOS_VALIDOS = ["aula_regular", "laboratorio", "sala_computo", "gimnasio", "taller"]
DIAS_VALIDOS     = ["lunes", "martes", "miercoles", "jueves", "viernes"]
NIVELES_VALIDOS  = [10, 11, 12]


class MateriaCreate(BaseModel):
    nombre:              str
    codigo:              str
    tipo:                str
    lecciones_semanales: int
    requiere_espacio:    str        = "aula_regular"
    bloques_por_sesion:  int        = 1
    niveles_aplicables:  List[int]  = [10, 11, 12]
    especialidad_id:     Optional[int] = None        # NULL = académica compartida
    dias_permitidos:     List[str]  = []

    @field_validator("tipo")
    def validar_tipo(cls, v):
        if v not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido. Debe ser: {TIPOS_VALIDOS}")
        return v

    @field_validator("bloques_por_sesion")
    def validar_bloques(cls, v):
        if v not in [3, 6, 9, 12]:
            raise ValueError("bloques_por_sesion debe ser 3, 6, 9 o 12")
        return v

    @field_validator("requiere_espacio")
    def validar_espacio(cls, v):
        if v not in ESPACIOS_VALIDOS:
            raise ValueError(f"Espacio inválido. Debe ser: {ESPACIOS_VALIDOS}")
        return v

    @field_validator("dias_permitidos")
    def validar_dias(cls, v):
        for dia in v:
            if dia not in DIAS_VALIDOS:
                raise ValueError(f"Día inválido: {dia}")
        return v

    @field_validator("niveles_aplicables")
    def validar_niveles(cls, v):
        if not v:
            raise ValueError("Debe seleccionar al menos un nivel")
        for n in v:
            if n not in NIVELES_VALIDOS:
                raise ValueError(f"Nivel inválido: {n}. Debe ser 10, 11 o 12")
        return sorted(set(v))

    @field_validator("lecciones_semanales")
    def validar_lecciones(cls, v):
        if not 1 <= v <= 40:
            raise ValueError("Las lecciones semanales deben estar entre 1 y 40")
        return v


class MateriaUpdate(BaseModel):
    nombre:              Optional[str]       = None
    tipo:                Optional[str]       = None
    lecciones_semanales: Optional[int]       = None
    requiere_espacio:    Optional[str]       = None
    bloques_por_sesion:  Optional[int]       = None
    niveles_aplicables:  Optional[List[int]] = None
    especialidad_id:     Optional[int]       = None
    dias_permitidos:     Optional[List[str]] = None
    activo:              Optional[bool]      = None


class MateriaResponse(BaseModel):
    id:                  int
    nombre:              str
    codigo:              str
    tipo:                str
    lecciones_semanales: int
    requiere_espacio:    str
    bloques_por_sesion:  int
    es_tecnica:          bool       = False
    niveles_aplicables:  List[int]  = [10, 11, 12]
    especialidad_id:     Optional[int] = None
    activo:              bool
    dias_permitidos:     List[str]  = []

    class Config: from_attributes = True
