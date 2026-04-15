from pydantic import BaseModel
from typing import Optional

# Lo que se recibe al CREAR
class EspecialidadCreate(BaseModel):
    nombre: str
    codigo: str

# Lo que se recibe al ACTUALIZAR (todo opcional)
class EspecialidadUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    activo: Optional[bool] = None

# Lo que se DEVUELVE al frontend
class EspecialidadResponse(BaseModel):
    id:     int
    nombre: str
    codigo: str
    activo: bool

    class Config: from_attributes = True  # permite convertir modelo SQLAlchemy a schema