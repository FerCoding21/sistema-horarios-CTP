from pydantic import BaseModel

class ResponseBase(BaseModel):
    """Schema base para respuestas exitosas"""
    mensaje: str
    exito: bool = True