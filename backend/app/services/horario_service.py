from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.horario  import Horario
from app.models.grupo    import Grupo
from app.models.materia  import Materia
from app.algorithm.generador import GeneradorHorarios

# Leccion de inicio de cada bloque (1→A, 2→B, 3→C, 4→D)
BLOQUE_A_LECCION = {1: 1, 2: 4, 3: 7, 4: 10}


def generar_horario(db: Session, anno_lectivo: int) -> dict:
    generador = GeneradorHorarios(db, anno_lectivo)
    return generador.generar()


def obtener_horario_grupo(db: Session, grupo_id: int, anno_lectivo: int):
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail=f"Grupo {grupo_id} no encontrado")

    lecciones = db.query(Horario).filter(
        Horario.grupo_id     == grupo_id,
        Horario.anno_lectivo == anno_lectivo
    ).order_by(Horario.dia, Horario.leccion_inicio).all()

    return _formatear_horario(lecciones)


def obtener_horario_completo(db: Session, anno_lectivo: int):
    lecciones = db.query(Horario).filter(
        Horario.anno_lectivo == anno_lectivo
    ).order_by(Horario.grupo_id, Horario.dia, Horario.leccion_inicio).all()

    return _formatear_horario(lecciones)


def modificar_leccion(db: Session, leccion_id: int, datos: dict):
    leccion = db.query(Horario).filter(Horario.id == leccion_id).first()
    if not leccion:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    nuevo_dia  = datos.get("dia",    leccion.dia)
    nuevo_bloque = datos.get("bloque", leccion.bloque)

    # Calcular leccion_inicio y leccion_fin a partir del bloque
    nueva_lec_ini = BLOQUE_A_LECCION.get(nuevo_bloque, leccion.leccion_inicio)
    bps           = leccion.leccion_fin - leccion.leccion_inicio + 1
    nueva_lec_fin = nueva_lec_ini + bps - 1

    # Determinar la pista (track) de la sesión que se mueve
    mat = db.query(Materia).filter(Materia.id == leccion.materia_id).first()
    esp_id_leccion = mat.especialidad_id if mat else None

    # Verificar conflicto según pista:
    # - Materia compartida (esp_id=None): no puede coincidir con NINGUNA otra sesión
    # - Materia de pista (esp_id≠None): no puede coincidir con sesiones de la MISMA pista
    lecs_nuevas = set(range(nueva_lec_ini, nueva_lec_fin + 1))

    sesiones_destino = db.query(Horario).filter(
        Horario.grupo_id     == leccion.grupo_id,
        Horario.dia          == nuevo_dia,
        Horario.anno_lectivo == leccion.anno_lectivo,
        Horario.id           != leccion_id
    ).all()

    for otra in sesiones_destino:
        lecs_otra = set(range(otra.leccion_inicio, otra.leccion_fin + 1))
        if not lecs_nuevas.intersection(lecs_otra):
            continue  # no solapan en tiempo

        mat_otra = db.query(Materia).filter(Materia.id == otra.materia_id).first()
        esp_id_otra = mat_otra.especialidad_id if mat_otra else None

        # Conflicto real si:
        # a) la sesión que muevo es compartida (afecta los 30 alumnos)
        # b) la otra sesión es compartida (afecta los 30 alumnos)
        # c) ambas son de la misma pista de especialidad
        if esp_id_leccion is None or esp_id_otra is None or esp_id_leccion == esp_id_otra:
            raise HTTPException(
                status_code=400,
                detail="Conflicto — hay otra sesión en ese horario para este grupo"
            )

    leccion.dia            = nuevo_dia
    leccion.bloque         = nuevo_bloque
    leccion.leccion_inicio = nueva_lec_ini
    leccion.leccion_fin    = nueva_lec_fin
    leccion.es_manual      = True
    db.commit()
    db.refresh(leccion)
    return {"mensaje": "Lección modificada correctamente", "exito": True}


def _formatear_horario(lecciones: list) -> list:
    return [
        {
            "id":              l.id,
            "dia":             l.dia,
            "bloque":          l.bloque,
            "leccion_inicio":  l.leccion_inicio,
            "leccion_fin":     l.leccion_fin,
            "grupo":           l.grupo.nombre             if l.grupo   else None,
            "grupo_id":        l.grupo_id,
            "materia":         l.materia.nombre           if l.materia else None,
            "materia_id":      l.materia_id,
            "especialidad_id": l.materia.especialidad_id  if l.materia else None,
            "es_manual":       l.es_manual,
            "anno_lectivo":    l.anno_lectivo,
        }
        for l in lecciones
    ]
