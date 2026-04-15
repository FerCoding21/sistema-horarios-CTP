from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    rol:          str
    nombre:       str
    email:        str

class UsuarioCreate(BaseModel):
    nombre:      str
    email:       EmailStr
    password:    str
    rol:         str          = "docente"
    profesor_id: Optional[int] = None

    @field_validator("rol")
    def validar_rol(cls, v):
        if v not in ["admin", "docente", "consulta"]:
            raise ValueError("Rol inválido. Debe ser: admin, docente o consulta")
        return v

    @field_validator("password")
    def validar_password(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

class UsuarioUpdate(BaseModel):
    nombre:  Optional[str]  = None
    activo:  Optional[bool] = None

class UsuarioResponse(BaseModel):
    id:          int
    nombre:      str
    email:       str
    rol:         str
    profesor_id: Optional[int] = None
    activo:      bool

    class Config:
        from_attributes = True

class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nuevo:  str

    @field_validator("password_nuevo")
    def validar_password(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

class SolicitarResetRequest(BaseModel):
    email: EmailStr

class ConfirmarResetRequest(BaseModel):
    email:          EmailStr
    otp:            str
    password_nuevo: str

    @field_validator("password_nuevo")
    def validar_password(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v