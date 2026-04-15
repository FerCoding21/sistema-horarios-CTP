from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database       import get_db
from app.auth           import get_admin, get_usuario_actual
from app.models.usuario import Usuario
from app.services       import horario_service

router = APIRouter(prefix="/horarios", tags=["Horarios"])


@router.post("/generar", status_code=status.HTTP_200_OK)
def generar_horario(
    anno_lectivo: int,
    _: Usuario = Depends(get_admin),
    db: Session = Depends(get_db)
):
    """Dispara el algoritmo de generación automática. Solo administradores."""
    return horario_service.generar_horario(db, anno_lectivo)


@router.get("/grupo/{grupo_id}")
def horario_por_grupo(
    grupo_id:     int,
    anno_lectivo: int,
    _: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db)
):
    return horario_service.obtener_horario_grupo(db, grupo_id, anno_lectivo)


@router.get("/completo")
def horario_completo(
    anno_lectivo: int,
    _: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db)
):
    return horario_service.obtener_horario_completo(db, anno_lectivo)


@router.patch("/leccion/{leccion_id}")
def modificar_leccion(
    leccion_id: int,
    datos: dict,
    _: Usuario = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return horario_service.modificar_leccion(db, leccion_id, datos)
