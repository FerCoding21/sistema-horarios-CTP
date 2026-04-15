from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario   import Usuario
from app.models.otp_reset import OtpReset
from app.schemas.usuario  import (UsuarioCreate, CambiarPasswordRequest,
                                   SolicitarResetRequest, ConfirmarResetRequest)
from app.auth             import hashear_password, verificar_password, crear_token
from app.services.email_service import enviar_otp_reset
from datetime             import timedelta, datetime, timezone
from app.config           import settings
import secrets, logging

logger = logging.getLogger(__name__)
OTP_EXPIRE_MINUTES = 15

def login(db: Session, email: str, password: str):
    """Autentica un usuario y devuelve un token JWT"""

    # Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    # Mismo mensaje de error para email y password incorrectos
    # Esto evita que un atacante sepa si el email existe o no
    error_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email o contraseña incorrectos",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if not usuario:
        raise error_credenciales

    if not verificar_password(password, usuario.password_hash):
        raise error_credenciales

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está desactivada. Contactá al administrador."
        )

    # Generar token
    token = crear_token(
        data={"sub": usuario.email, "rol": usuario.rol},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return {
        "access_token": token,
        "token_type":   "bearer",
        "rol":          usuario.rol,
        "nombre":       usuario.nombre,
        "email":        usuario.email
    }


def crear_usuario(db: Session, datos: UsuarioCreate):
    """Crea un nuevo usuario del sistema"""

    # Verificar email duplicado
    existe = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario con el email {datos.email}"
        )

    # Si se vincula a un profesor, verificar que no tenga usuario ya
    if datos.profesor_id:
        from app.models.profesor import Profesor
        profesor = db.query(Profesor)\
                     .filter(Profesor.id == datos.profesor_id)\
                     .first()
        if not profesor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profesor con ID {datos.profesor_id} no encontrado"
            )

        usuario_existente = db.query(Usuario)\
                              .filter(Usuario.profesor_id == datos.profesor_id)\
                              .first()
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este profesor ya tiene un usuario asignado"
            )

    nuevo = Usuario(
        nombre        = datos.nombre,
        email         = datos.email,
        password_hash = hashear_password(datos.password),
        rol           = datos.rol,
        profesor_id   = datos.profesor_id
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def cambiar_password(db: Session, usuario: Usuario,
                     datos: CambiarPasswordRequest):
    """Permite a un usuario cambiar su propia contraseña"""

    if not verificar_password(datos.password_actual, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )

    usuario.password_hash = hashear_password(datos.password_nuevo)
    db.commit()
    return {"mensaje": "Contraseña actualizada correctamente"}


def listar_usuarios(db: Session):
    return db.query(Usuario).order_by(Usuario.nombre).all()


def desactivar_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya se encuentra inactivo"
        )
    usuario.activo = False
    db.commit()
    return {"mensaje": f"Usuario {usuario.email} desactivado correctamente"}


# ── Password Reset con OTP ────────────────────────────────────────

def solicitar_reset(db: Session, datos: SolicitarResetRequest) -> dict:
    """
    Genera un OTP de 6 dígitos, lo almacena hasheado y lo envía por correo.
    Siempre responde con el mismo mensaje (no revela si el email existe).
    """
    MSG_GENERICO = {"mensaje": "Si el correo existe en el sistema, recibirás un código en breve."}

    usuario = db.query(Usuario).filter(
        Usuario.email  == datos.email,
        Usuario.activo == True
    ).first()

    if not usuario:
        return MSG_GENERICO

    # Solo admins pueden usar reset por OTP
    if usuario.rol != "admin":
        return MSG_GENERICO

    # Invalidar OTPs anteriores del mismo email
    db.query(OtpReset).filter(
        OtpReset.email == datos.email,
        OtpReset.usado == False
    ).update({"usado": True})

    # Generar OTP de 6 dígitos
    otp_plano = f"{secrets.randbelow(1_000_000):06d}"
    otp_hash  = hashear_password(otp_plano)

    db.add(OtpReset(email=datos.email, otp_hash=otp_hash))
    db.commit()

    try:
        enviar_otp_reset(usuario.email, usuario.nombre, otp_plano)
    except Exception as e:
        logger.error(f"Error al enviar OTP a {usuario.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo enviar el correo. Verificá la configuración SMTP en el servidor."
        )

    return MSG_GENERICO


def confirmar_reset(db: Session, datos: ConfirmarResetRequest) -> dict:
    """Verifica el OTP y actualiza la contraseña."""

    ahora = datetime.now(timezone.utc)
    limite = ahora - timedelta(minutes=OTP_EXPIRE_MINUTES)

    # Buscar OTPs válidos (no usados, no expirados) para este email
    otps = db.query(OtpReset).filter(
        OtpReset.email  == datos.email,
        OtpReset.usado  == False,
        OtpReset.created_at >= limite
    ).order_by(OtpReset.created_at.desc()).all()

    otp_valido = None
    for otp_registro in otps:
        if verificar_password(datos.otp, otp_registro.otp_hash):
            otp_valido = otp_registro
            break

    if not otp_valido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código incorrecto o expirado."
        )

    # Marcar OTP como usado
    otp_valido.usado = True

    # Actualizar contraseña
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    usuario.password_hash = hashear_password(datos.password_nuevo)
    db.commit()
    return {"mensaje": "Contraseña restablecida correctamente."}