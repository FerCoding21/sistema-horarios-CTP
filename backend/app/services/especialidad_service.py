from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.especialidad  import Especialidad
from app.schemas.especialidad import EspecialidadCreate, EspecialidadUpdate

def obtener_especialidades(db: Session, solo_activas: bool = True):
    query = db.query(Especialidad)
    if solo_activas:
        query = query.filter(Especialidad.activo == True)
    return query.order_by(Especialidad.nombre).all()


def obtener_especialidad_por_id(db: Session, especialidad_id: int):
    especialidad = db.query(Especialidad)\
                     .filter(Especialidad.id == especialidad_id).first()
    if not especialidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Especialidad con ID {especialidad_id} no encontrada"
        )
    return especialidad


def crear_especialidad(db: Session, datos: EspecialidadCreate):
    existe = db.query(Especialidad)\
               .filter(Especialidad.codigo == datos.codigo).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una especialidad con el código {datos.codigo}"
        )
    try:
        nueva = Especialidad(
            nombre = datos.nombre,
            codigo = datos.codigo
        )
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return nueva
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la especialidad"
        )


def actualizar_especialidad(db: Session, especialidad_id: int,
                             datos: EspecialidadUpdate):
    especialidad = obtener_especialidad_por_id(db, especialidad_id)
    campos = datos.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        setattr(especialidad, campo, valor)
    db.commit()
    db.refresh(especialidad)
    return especialidad


def desactivar_especialidad(db: Session, especialidad_id: int):
    especialidad = obtener_especialidad_por_id(db, especialidad_id)
    if not especialidad.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La especialidad ya está inactiva"
        )
    especialidad.activo = False
    db.commit()
    return {"mensaje": f"Especialidad {especialidad.nombre} desactivada correctamente"}