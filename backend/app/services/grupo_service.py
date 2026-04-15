from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.grupo        import Grupo
from app.models.especialidad import Especialidad
from app.schemas.grupo       import GrupoCreate, GrupoUpdate
from typing import List


def _cargar_especialidades(db: Session, ids: List[int]) -> List[Especialidad]:
    result = []
    for eid in ids:
        esp = db.query(Especialidad).filter(Especialidad.id == eid).first()
        if not esp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Especialidad con ID {eid} no encontrada"
            )
        result.append(esp)
    return result


def obtener_grupos(db: Session, solo_activos: bool = True):
    query = db.query(Grupo)
    if solo_activos:
        query = query.filter(Grupo.activo == True)
    return query.order_by(Grupo.nivel, Grupo.seccion).all()


def obtener_grupo_por_id(db: Session, grupo_id: int):
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grupo con ID {grupo_id} no encontrado"
        )
    return grupo


def crear_grupo(db: Session, datos: GrupoCreate):
    if db.query(Grupo).filter(Grupo.nombre == datos.nombre).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un grupo con el nombre {datos.nombre}"
        )

    especialidades = _cargar_especialidades(db, datos.especialidad_ids)

    try:
        nuevo_grupo = Grupo(
            nombre          = datos.nombre,
            nivel           = datos.nivel,
            seccion         = datos.seccion,
            num_estudiantes = datos.num_estudiantes,
            tipo_horario    = datos.tipo_horario,
        )
        nuevo_grupo.especialidades = especialidades
        db.add(nuevo_grupo)
        db.commit()
        db.refresh(nuevo_grupo)
        return nuevo_grupo

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el grupo — verifique que no exista ya"
        )


def actualizar_grupo(db: Session, grupo_id: int, datos: GrupoUpdate):
    grupo  = obtener_grupo_por_id(db, grupo_id)
    campos = datos.model_dump(exclude_unset=True, exclude={"especialidad_ids"})
    for campo, valor in campos.items():
        setattr(grupo, campo, valor)

    if datos.especialidad_ids is not None:
        grupo.especialidades = _cargar_especialidades(db, datos.especialidad_ids)

    db.commit()
    db.refresh(grupo)
    return grupo


def desactivar_grupo(db: Session, grupo_id: int):
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El grupo ya se encuentra inactivo"
        )
    grupo.activo = False
    db.commit()
    return {"mensaje": f"Grupo {grupo.nombre} desactivado correctamente"}
