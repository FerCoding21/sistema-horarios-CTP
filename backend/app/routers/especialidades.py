from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database        import get_db
from app.auth            import get_usuario_actual, get_admin
from app.models.usuario  import Usuario
from app.schemas         import (EspecialidadCreate, EspecialidadUpdate,
                                  EspecialidadResponse, ResponseBase)
from app.services        import especialidad_service
from typing import List

router = APIRouter(
    prefix="/especialidades",
    tags=["Especialidades"]
)


@router.get("/", response_model=List[EspecialidadResponse])
def listar_especialidades(
    solo_activas: bool = True,
    _: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db)
):
    return especialidad_service.obtener_especialidades(db, solo_activas)


@router.get("/{especialidad_id}", response_model=EspecialidadResponse)
def obtener_especialidad(
    especialidad_id: int,
    _: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db)
):
    return especialidad_service.obtener_especialidad_por_id(db, especialidad_id)


@router.post("/", response_model=EspecialidadResponse,
             status_code=status.HTTP_201_CREATED)
def crear_especialidad(
    datos: EspecialidadCreate,
    _: Usuario = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return especialidad_service.crear_especialidad(db, datos)


@router.put("/{especialidad_id}", response_model=EspecialidadResponse)
def actualizar_especialidad(
    especialidad_id: int,
    datos: EspecialidadUpdate,
    _: Usuario = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return especialidad_service.actualizar_especialidad(db, especialidad_id, datos)


@router.delete("/{especialidad_id}", response_model=ResponseBase)
def desactivar_especialidad(
    especialidad_id: int,
    _: Usuario = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return especialidad_service.desactivar_especialidad(db, especialidad_id)