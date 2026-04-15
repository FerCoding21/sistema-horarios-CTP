from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas  import MateriaCreate, MateriaUpdate, MateriaResponse, ResponseBase
from app.services import materia_service
from typing import List
from app.auth import get_usuario_actual, get_admin
from app.models.usuario import Usuario

router = APIRouter(prefix="/materias", tags=["Materias"])


def _serializar(m, dias: list) -> dict:
    return {
        "id":                  m.id,
        "nombre":              m.nombre,
        "codigo":              m.codigo,
        "tipo":                m.tipo,
        "lecciones_semanales": m.lecciones_semanales,
        "requiere_espacio":    m.requiere_espacio,
        "bloques_por_sesion":  m.bloques_por_sesion,
        "es_tecnica":          m.es_tecnica,
        "niveles_aplicables":  m.niveles_aplicables or [10, 11, 12],
        "especialidad_id":     m.especialidad_id,
        "activo":              m.activo,
        "dias_permitidos":     dias,
    }


@router.get("/", response_model=List[MateriaResponse])
def listar_materias(
    solo_activas: bool = True,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_actual)
):
    materias = materia_service.obtener_materias(db, solo_activas)
    return [_serializar(m, materia_service.obtener_dias_permitidos(db, m.id)) for m in materias]


@router.get("/{materia_id}", response_model=MateriaResponse)
def obtener_materia(materia_id: int, db: Session = Depends(get_db)):
    m = materia_service.obtener_materia_por_id(db, materia_id)
    return _serializar(m, materia_service.obtener_dias_permitidos(db, materia_id))


@router.post("/", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
def crear_materia(
    datos: MateriaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_admin)
):
    m = materia_service.crear_materia(db, datos)
    return _serializar(m, materia_service.obtener_dias_permitidos(db, m.id))


@router.put("/{materia_id}", response_model=MateriaResponse)
def actualizar_materia(
    materia_id: int,
    datos: MateriaUpdate,
    db: Session = Depends(get_db)
):
    m = materia_service.actualizar_materia(db, materia_id, datos)
    return _serializar(m, materia_service.obtener_dias_permitidos(db, materia_id))


@router.delete("/{materia_id}", response_model=ResponseBase)
def desactivar_materia(materia_id: int, db: Session = Depends(get_db)):
    return materia_service.desactivar_materia(db, materia_id)
