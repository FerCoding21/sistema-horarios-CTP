from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.materia  import Materia, MateriaDiaPermitido
from app.schemas.materia import MateriaCreate, MateriaUpdate
from typing import List


def obtener_materias(db: Session, solo_activas: bool = True):
    query = db.query(Materia)
    if solo_activas:
        query = query.filter(Materia.activo == True)
    return query.order_by(Materia.nombre).all()


def obtener_materia_por_id(db: Session, materia_id: int):
    materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if not materia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Materia con ID {materia_id} no encontrada"
        )
    return materia


def crear_materia(db: Session, datos: MateriaCreate):
    if db.query(Materia).filter(Materia.codigo == datos.codigo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una materia con el código {datos.codigo}"
        )

    try:
        nueva_materia = Materia(
            nombre              = datos.nombre,
            codigo              = datos.codigo,
            tipo                = datos.tipo,
            lecciones_semanales = datos.lecciones_semanales,
            requiere_espacio    = datos.requiere_espacio,
            bloques_por_sesion  = datos.bloques_por_sesion,
            es_tecnica          = datos.tipo == "tecnica",
            niveles_aplicables  = datos.niveles_aplicables,
            especialidad_id     = datos.especialidad_id,
        )
        db.add(nueva_materia)
        db.flush()

        if datos.dias_permitidos:
            db.add_all([
                MateriaDiaPermitido(materia_id=nueva_materia.id, dia=dia)
                for dia in datos.dias_permitidos
            ])

        db.commit()
        db.refresh(nueva_materia)
        return nueva_materia

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad al crear la materia"
        )


def actualizar_materia(db: Session, materia_id: int, datos: MateriaUpdate):
    materia = obtener_materia_por_id(db, materia_id)

    campos = datos.model_dump(exclude_unset=True, exclude={"dias_permitidos"})
    for campo, valor in campos.items():
        setattr(materia, campo, valor)
    # es_tecnica siempre deriva del tipo
    if "tipo" in campos:
        materia.es_tecnica = materia.tipo == "tecnica"

    if datos.dias_permitidos is not None:
        db.query(MateriaDiaPermitido)\
          .filter(MateriaDiaPermitido.materia_id == materia_id)\
          .delete()
        if datos.dias_permitidos:
            db.add_all([
                MateriaDiaPermitido(materia_id=materia_id, dia=dia)
                for dia in datos.dias_permitidos
            ])

    db.commit()
    db.refresh(materia)
    return materia


def desactivar_materia(db: Session, materia_id: int):
    materia = obtener_materia_por_id(db, materia_id)
    if not materia.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La materia ya se encuentra inactiva"
        )
    materia.activo = False
    db.commit()
    return {"mensaje": f"Materia {materia.nombre} desactivada correctamente"}


def obtener_dias_permitidos(db: Session, materia_id: int) -> List[str]:
    obtener_materia_por_id(db, materia_id)
    return [
        d.dia for d in
        db.query(MateriaDiaPermitido)
          .filter(MateriaDiaPermitido.materia_id == materia_id).all()
    ]
