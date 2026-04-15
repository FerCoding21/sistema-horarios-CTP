from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas  import GrupoCreate, GrupoUpdate, GrupoResponse, ResponseBase
from app.services import grupo_service
from typing import List
from app.auth import get_usuario_actual, get_admin
from app.models.usuario import Usuario

router = APIRouter(prefix="/grupos", tags=["Grupos"])


@router.get("/", response_model=List[GrupoResponse])
def listar_grupos(
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_actual)
):
    return grupo_service.obtener_grupos(db, solo_activos)


@router.get("/{grupo_id}", response_model=GrupoResponse)
def obtener_grupo(grupo_id: int, db: Session = Depends(get_db)):
    return grupo_service.obtener_grupo_por_id(db, grupo_id)


@router.post("/", response_model=GrupoResponse, status_code=status.HTTP_201_CREATED)
def crear_grupo(
    datos: GrupoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_admin)
):
    return grupo_service.crear_grupo(db, datos)


@router.put("/{grupo_id}", response_model=GrupoResponse)
def actualizar_grupo(
    grupo_id: int,
    datos: GrupoUpdate,
    db: Session = Depends(get_db)
):
    return grupo_service.actualizar_grupo(db, grupo_id, datos)


@router.delete("/{grupo_id}", response_model=ResponseBase)
def desactivar_grupo(grupo_id: int, db: Session = Depends(get_db)):
    return grupo_service.desactivar_grupo(db, grupo_id)
