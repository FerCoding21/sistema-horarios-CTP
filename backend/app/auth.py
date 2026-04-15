from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config   import settings
from app.database import get_db
from app.models.usuario import Usuario

# Configuración de hashing de contraseñas
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# Esquema OAuth2 — indica a FastAPI dónde buscar el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ─────────────────────────────────────────────
# MANEJO DE CONTRASEÑAS
# ─────────────────────────────────────────────
def hashear_password(password: str) -> str:
    """Convierte una contraseña en texto plano a hash bcrypt"""
    return pwd_context.hash(password)


def verificar_password(password_plano: str, password_hash: str) -> bool:
    """Verifica si una contraseña coincide con su hash"""
    return pwd_context.verify(password_plano, password_hash)


# ─────────────────────────────────────────────
# MANEJO DE TOKENS JWT
# ─────────────────────────────────────────────
def crear_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT firmado"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=480)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, 
                      algorithm=settings.algorithm)


def verificar_token(token: str) -> dict:
    """Decodifica y verifica un token JWT"""
    try:
        payload = jwt.decode(token, settings.secret_key,
                             algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )


# ─────────────────────────────────────────────
# DEPENDENCIAS DE AUTENTICACIÓN
# ─────────────────────────────────────────────
def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia que extrae el usuario del token.
    Se usa en cualquier endpoint que requiera autenticación.
    """
    payload = verificar_token(token)
    email   = payload.get("sub")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido — no contiene usuario"
        )

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario del token no encontrado"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return usuario


def get_admin(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """
    Dependencia que verifica que el usuario sea administrador.
    Usala en endpoints que solo admins pueden usar.
    """
    if usuario.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permisos para realizar esta acción"
        )
    return usuario


def get_admin_o_docente(
    usuario: Usuario = Depends(get_usuario_actual)
) -> Usuario:
    """
    Dependencia para endpoints que admins y docentes pueden usar.
    """
    if usuario.rol not in ["admin", "docente"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permisos para realizar esta acción"
        )
    return usuario