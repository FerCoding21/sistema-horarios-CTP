"""
Diagnostico de viabilidad del horario (modelo de pistas paralelas).
Ejecutar desde backend/: python diagnostico.py
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.grupo   import Grupo
from app.models.materia import Materia

db = SessionLocal()
grupos         = db.query(Grupo).filter(Grupo.activo == True).order_by(Grupo.nivel, Grupo.seccion).all()
todas_materias = db.query(Materia).filter(Materia.activo == True).all()

print(f"\n{'='*100}")
print(f"DIAGNOSTICO DE VIABILIDAD (pistas paralelas) -- {len(grupos)} grupos, {len(todas_materias)} materias activas")
print(f"{'='*100}\n")

hay_problemas = False

for grupo in grupos:
    esp_ids = {e.id for e in grupo.especialidades}
    es_multi = len(esp_ids) > 1

    # Lecciones compartidas (academicas sin esp_id)
    shared_lec = 0
    # Lecciones por pista de especialidad
    pista_lec  = {}   # esp_id -> lecciones efectivas

    detalles = []

    for m in todas_materias:
        niveles = m.niveles_aplicables or [10, 11, 12]
        if grupo.nivel not in niveles:
            continue
        if m.especialidad_id is not None and m.especialidad_id not in esp_ids:
            continue
        if m.es_tecnica and not esp_ids:
            continue

        bps       = m.bloques_por_sesion
        sesiones  = math.ceil(m.lecciones_semanales / bps)
        lec_efect = sesiones * bps

        if m.especialidad_id is not None and es_multi:
            pista_lec[m.especialidad_id] = pista_lec.get(m.especialidad_id, 0) + lec_efect
        elif m.especialidad_id is not None and not es_multi:
            # grupo de una sola especialidad: tecnicas van al pool total
            shared_lec += lec_efect
        else:
            # academica pura (sin esp_id)
            shared_lec += lec_efect

        detalles.append((m.nombre, m.tipo, m.especialidad_id, m.lecciones_semanales, lec_efect, bps))

    # Tiempo total requerido = compartidas + max(pistas) para grupos multi
    if es_multi and pista_lec:
        max_pista = max(pista_lec.values())
        tiempo    = shared_lec + max_pista
    else:
        tiempo    = shared_lec

    problemas = []
    if tiempo > 60:
        problemas.append(f"EXCEDE ({tiempo})")

    estado = 'OK' if not problemas else ('ERROR: ' + ' | '.join(problemas))

    esp_nombres = ', '.join(e.nombre for e in grupo.especialidades) or '--'
    tipo_label  = 'MULTI' if es_multi else ('1-ESP' if esp_ids else 'ACAD')

    if es_multi:
        pista_str = ' '.join(f"esp{eid}={lec}" for eid, lec in sorted(pista_lec.items()))
        print(f"  {grupo.nombre:<8} {tipo_label}  shared={shared_lec} {pista_str} => tiempo={tiempo} {estado}")
    else:
        print(f"  {grupo.nombre:<8} {tipo_label}  total={tiempo} {estado}")

    if problemas:
        hay_problemas = True
        print(f"  Detalle materias ({grupo.nombre}):")
        for nombre, tipo_m, esp_id, lec_orig, lec_ef, bps in sorted(detalles, key=lambda x: -x[4]):
            flag = ' <- bps rounding' if lec_ef != lec_orig else ''
            pista = f'[esp{esp_id}]' if esp_id else '[shared]'
            print(f"    {pista} {'[TEC]' if tipo_m=='tecnica' else '[GEN]'} {nombre:<40} {lec_orig} lec -> {lec_ef} ef (bps={bps}){flag}")
    print()

if not hay_problemas:
    print("Todos los grupos son viables en capacidad.")
else:
    print("Hay grupos que exceden los 60 slots disponibles.")

db.close()
