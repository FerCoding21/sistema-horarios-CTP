from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database        import get_db
from app.auth            import get_usuario_actual, get_admin
from app.schemas.usuario import (TokenResponse, UsuarioCreate, UsuarioResponse,
                                  CambiarPasswordRequest, SolicitarResetRequest,
                                  ConfirmarResetRequest)
from app.services        import auth_service
from app.models.usuario  import Usuario
from typing import List

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login del sistema. Devuelve token JWT.
    Usá el email como username en el formulario.
    """
    return auth_service.login(db, form_data.username, form_data.password)


@router.get("/me", response_model=UsuarioResponse)
def mi_perfil(
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    """Devuelve los datos del usuario autenticado"""
    return usuario_actual


@router.post("/cambiar-password")
def cambiar_password(
    datos: CambiarPasswordRequest,
    usuario_actual: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db)
):
    """Permite cambiar la contraseña del usuario autenticado"""
    return auth_service.cambiar_password(db, usuario_actual, datos)


@router.post("/usuarios", response_model=UsuarioResponse,
             status_code=status.HTTP_201_CREATED)
def crear_usuario(
    datos: UsuarioCreate,
    _: Usuario = Depends(get_admin),     # solo admins pueden crear usuarios
    db: Session = Depends(get_db)
):
    """Crea un nuevo usuario — solo administradores"""
    return auth_service.crear_usuario(db, datos)


@router.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios(
    _: Usuario = Depends(get_admin),
    db: Session = Depends(get_db)
):
    """Lista todos los usuarios — solo administradores"""
    return auth_service.listar_usuarios(db)


@router.delete("/usuarios/{usuario_id}")
def desactivar_usuario(
    usuario_id: int,
    _: Usuario = Depends(get_admin),
    db: Session = Depends(get_db)
):
    """Desactiva un usuario — solo administradores"""
    return auth_service.desactivar_usuario(db, usuario_id)


# ── Password Reset con OTP (sin autenticación previa) ────────────

@router.post("/solicitar-reset")
def solicitar_reset(datos: SolicitarResetRequest, db: Session = Depends(get_db)):
    """
    Envía un código OTP de 6 dígitos al correo del administrador.
    Solo funciona para cuentas con rol 'admin'.
    """
    return auth_service.solicitar_reset(db, datos)


@router.post("/confirmar-reset")
def confirmar_reset(datos: ConfirmarResetRequest, db: Session = Depends(get_db)):
    """
    Verifica el OTP y actualiza la contraseña.
    El código expira a los 15 minutos y es de un solo uso.
    """
    return auth_service.confirmar_reset(db, datos)