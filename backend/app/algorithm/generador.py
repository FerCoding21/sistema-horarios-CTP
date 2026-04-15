from ortools.sat.python import cp_model
from sqlalchemy.orm import Session
from app.models.grupo   import Grupo
from app.models.materia import Materia, MateriaDiaPermitido
from app.models.horario import Horario
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes"]

# ── Estructura de lecciones del CTP ───────────────────────────
# 12 lecciones por día en 4 bloques de 3 lecciones cada uno
# Bloque A: 1-2-3   → 7:00 a 9:00
# Bloque B: 4-5-6   → 9:20 a 11:20
# Bloque C: 7-8-9   → 12:00 a 2:00
# Bloque D: 10-11-12 → 2:20 a 4:20

TODAS_LECCIONES = list(range(1, 13))
INICIO_TECNICO  = [1, 4, 7, 10]   # bloques completos de 3

# ── Slots permitidos por tipo de horario ──────────────────────
# Grupos 1-4 de cada nivel son "split": sus estudiantes se dividen
# entre dos especialidades técnicas que se alternan por días.
# Los grupos 5-10 son "general": sin restricción de días.

SLOTS_TECNICOS = {
    # split_10: técnicas en Lun + Mar + Mié(mañana)
    'split_10': {
        'lunes':     set(range(1, 13)),
        'martes':    set(range(1, 13)),
        'miercoles': set(range(1, 7)),   # bloques A y B
    },
    # split_11/12: técnicas solo en Lun + Mar
    'split_11': {
        'lunes':  set(range(1, 13)),
        'martes': set(range(1, 13)),
    },
    'split_12': {
        'lunes':  set(range(1, 13)),
        'martes': set(range(1, 13)),
    },
}

SLOTS_GENERALES = {
    'split_10': {
        'miercoles': set(range(7, 13)),  # bloques C y D
        'jueves':    set(range(1, 13)),
        'viernes':   set(range(1, 13)),
    },
    'split_11': {
        'miercoles': set(range(1, 13)),
        'jueves':    set(range(1, 13)),
        'viernes':   set(range(1, 13)),
    },
    'split_12': {
        'miercoles': set(range(1, 13)),
        'jueves':    set(range(1, 13)),
        'viernes':   set(range(1, 13)),
    },
}

LECCION_A_BLOQUE = {
    1:1, 2:1, 3:1,
    4:2, 5:2, 6:2,
    7:3, 8:3, 9:3,
    10:4, 11:4, 12:4,
}

LECCION_A_HORA = {
    1:  "7:00",  2:  "7:40",  3:  "8:20",
    4:  "9:20",  5:  "10:00", 6:  "10:40",
    7:  "12:00", 8:  "12:40", 9:  "1:20",
    10: "2:20",  11: "3:00",  12: "3:40",
}


class GeneradorHorarios:

    def __init__(self, db: Session, anno_lectivo: int):
        self.db           = db
        self.anno_lectivo = anno_lectivo
        self.modelo       = cp_model.CpModel()
        self.variables    = {}   # (gid, mid, dia, l_ini) → BoolVar
        self.resultado    = {}
        self.mat_cache    = {}   # mid → Materia

    # ─────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────
    def _slots_permitidos(self, tipo_horario: str, es_tecnica: bool):
        """Retorna {dia → set(lecciones)} o None si no hay restricción."""
        if tipo_horario == 'general':
            return None
        tabla = SLOTS_TECNICOS if es_tecnica else SLOTS_GENERALES
        return tabla.get(tipo_horario)

    def _lecciones_inicio_validas(self, lec: int) -> list:
        """
        Posiciones de inicio válidas para una sesión de 'lec' lecciones.

        - Múltiplo de 3 (1 o más bloques completos): solo inicio de bloque.
        - 2 lecciones: dentro del mismo bloque (pares: 1-2, 2-3, 4-5, 5-6, …).
        - 1 lección: cualquier posición.
        - Otro valor: cualquier posición donde la sesión quepa en el día.
        """
        if lec % 3 == 0:
            return [l for l in INICIO_TECNICO if l + lec - 1 <= 12]
        if lec == 1:
            return TODAS_LECCIONES
        if lec == 2:
            # pares válidos dentro del mismo bloque: (1,2),(2,3),(4,5),(5,6),(7,8),(8,9),(10,11),(11,12)
            return [b + i for b in [1, 4, 7, 10] for i in [0, 1]]
        # fallback genérico
        return [l for l in range(1, 13) if l + lec - 1 <= 12]

    def _lecciones_ocupadas(self, l_ini: int, lec: int) -> range:
        return range(l_ini, l_ini + lec)

    # ─────────────────────────────────────────────
    # PASO 1: CARGAR DATOS
    # ─────────────────────────────────────────────
    def _cargar_datos(self):
        logger.info("Cargando datos...")

        self.grupos       = self.db.query(Grupo).filter(Grupo.activo == True).all()
        self.grupos_por_id = {g.id: g for g in self.grupos}

        # Días restringidos por materia (si el usuario los configuró)
        self.dias_permitidos = {}
        for d in self.db.query(MateriaDiaPermitido).all():
            self.dias_permitidos.setdefault(d.materia_id, set()).add(d.dia)

        # Todas las materias activas (se filtran por grupo en el loop)
        todas_materias = self.db.query(Materia).filter(Materia.activo == True).all()
        esp_ids_por_grupo = {
            g.id: {e.id for e in g.especialidades}
            for g in self.grupos
        }

        # Construir lista de asignaciones derivadas automáticamente:
        # una materia aplica a un grupo si:
        #   1. el nivel del grupo está en niveles_aplicables de la materia
        #   2. es académica (especialidad_id IS NULL) O pertenece a una
        #      especialidad del grupo
        self.asignaciones = []
        for grupo in self.grupos:
            esp_ids = esp_ids_por_grupo[grupo.id]
            for materia in todas_materias:
                niveles = materia.niveles_aplicables or [10, 11, 12]
                if grupo.nivel not in niveles:
                    continue
                if materia.especialidad_id is not None \
                        and materia.especialidad_id not in esp_ids:
                    continue
                # materia técnica pero el grupo no tiene especialidades → saltar
                if materia.es_tecnica and not esp_ids:
                    continue

                self.mat_cache[materia.id] = materia

                # bps = bloques por sesión (1 bloque = 3 lecciones)
                # → cada sesión completa ocupa bps × 3 lecciones consecutivas
                lec_total          = materia.lecciones_semanales
                lec_por_sesion     = materia.bloques_por_sesion * 3
                sesiones_completas = lec_total // lec_por_sesion
                resto              = lec_total % lec_por_sesion

                if sesiones_completas > 0:
                    self.asignaciones.append({
                        "grupo":           grupo,
                        "materia":         materia,
                        "sesiones":        sesiones_completas,
                        "lec_per_session": lec_por_sesion,
                    })
                if resto > 0:
                    # Sesión parcial con las lecciones restantes
                    self.asignaciones.append({
                        "grupo":           grupo,
                        "materia":         materia,
                        "sesiones":        1,
                        "lec_per_session": resto,
                    })

        # ── Detectar pares gemelos ────────────────────────────────────
        # Dos grupos son "gemelos" si tienen el mismo nivel y el mismo
        # conjunto de especialidades. Aplica a cualquier tipo de horario.
        grupos_por_key = defaultdict(list)
        for g in self.grupos:
            if g.especialidades:
                key = (g.nivel, frozenset(e.id for e in g.especialidades))
                grupos_por_key[key].append(g)

        self.pares_gemelos = []
        for key, glist in grupos_por_key.items():
            if len(glist) >= 2:
                for i in range(0, len(glist) - 1, 2):
                    self.pares_gemelos.append((glist[i], glist[i+1]))
                    logger.info(f"Par gemelo: {glist[i].nombre} + {glist[i+1].nombre}")

        # Grupos con múltiples especialidades → pistas paralelas
        self.multi_esp_gids = {g.id for g in self.grupos if len(g.especialidades) > 1}

        logger.info(
            f"Grupos:{len(self.grupos)} | "
            f"Asignaciones:{len(self.asignaciones)} | "
            f"Pares gemelos:{len(self.pares_gemelos)}"
        )

    # ─────────────────────────────────────────────
    # PASO 2: CREAR VARIABLES
    # Variable = posible sesión (grupo, materia, dia, leccion_inicio)
    # ─────────────────────────────────────────────
    def _crear_variables(self):
        logger.info("Creando variables...")

        for asig in self.asignaciones:
            g   = asig["grupo"]
            m   = asig["materia"]
            lps = asig["lec_per_session"]   # lecciones que ocupa esta sesión

            lecciones_inicio = self._lecciones_inicio_validas(lps)
            # Para grupos multi-especialidad, cualquier materia con esp_id
            # pertenece a una pista de especialidad (usa slots técnicos).
            usa_slots_tec = m.es_tecnica or (
                m.especialidad_id is not None and g.id in self.multi_esp_gids
            )
            slots_grupo = self._slots_permitidos(g.tipo_horario, usa_slots_tec)

            for dia in DIAS:
                # Días restringidos para esta materia (configuración manual)
                if m.id in self.dias_permitidos:
                    if dia not in self.dias_permitidos[m.id]:
                        continue

                # Días permitidos según tipo_horario del grupo
                if slots_grupo is not None and dia not in slots_grupo:
                    continue

                for l_ini in lecciones_inicio:
                    ocupadas = list(self._lecciones_ocupadas(l_ini, lps))

                    # Verificar que todas las lecciones ocupadas caen en slots válidos
                    if slots_grupo is not None:
                        lecs_dia = slots_grupo.get(dia, set())
                        if not all(l in lecs_dia for l in ocupadas):
                            continue

                    clave = (g.id, m.id, lps, dia, l_ini)
                    if clave not in self.variables:
                        self.variables[clave] = self.modelo.NewBoolVar(
                            f"g{g.id}_m{m.id}_s{lps}_{dia}_l{l_ini}"
                        )

        logger.info(f"Variables creadas: {len(self.variables)}")
        if not self.variables:
            raise ValueError(
                "No se generaron variables. "
                "Verificá que las materias tengan niveles y especialidades configuradas "
                "y que los grupos tengan especialidades asignadas."
            )

    # ─────────────────────────────────────────────
    # PASO 3: RESTRICCIONES
    # ─────────────────────────────────────────────
    def _aplicar_restricciones(self):
        logger.info("Construyendo mapas de ocupación...")

        # ── Mapa de ocupación por pista ───────────────────────────────
        # Para grupos multi-especialidad, cada materia con esp_id corre en
        # una "pista" paralela (track_id = especialidad_id).
        # Las materias sin esp_id son compartidas (track_id = None).
        # Para grupos de una sola especialidad, todo va al mismo track (None).
        #
        # Clave: (gid, track_id, dia, lec) → lista de variables
        g_map = {}
        for (gid, mid, lps, dia, l_ini), var in self.variables.items():
            mat      = self.mat_cache[mid]
            track_id = mat.especialidad_id if gid in self.multi_esp_gids else None
            for lec in self._lecciones_ocupadas(l_ini, lps):
                g_map.setdefault((gid, track_id, dia, lec), []).append(var)

        # R1a: dentro de cada pista, máximo 1 materia por lección
        for (gid, track_id, dia, lec), vars_list in g_map.items():
            if len(vars_list) > 1:
                self.modelo.Add(sum(vars_list) <= 1)

        # R1b: en grupos multi-especialidad, una materia compartida (track=None)
        # no puede coincidir en el mismo slot con ninguna pista de especialidad.
        # (Las pistas entre sí SÍ pueden coincidir — son paralelas.)
        for gid in self.multi_esp_gids:
            grupo = self.grupos_por_id[gid]
            for dia in DIAS:
                for lec in range(1, 13):
                    acad_vars = g_map.get((gid, None, dia, lec), [])
                    if not acad_vars:
                        continue
                    for esp in grupo.especialidades:
                        tech_vars = g_map.get((gid, esp.id, dia, lec), [])
                        if not tech_vars:
                            continue
                        self.modelo.Add(sum(acad_vars) + sum(tech_vars) <= 1)

        # R2: conteo exacto de sesiones por (grupo, materia, tamaño de sesión)
        # Cada entrada de asignaciones tiene su propio lec_per_session
        # (sesiones completas y sesiones parciales son entradas distintas).
        gm_vars = defaultdict(list)
        for (gid, mid, lps, dia, l_ini), var in self.variables.items():
            gm_vars[(gid, mid, lps)].append(var)

        for asig in self.asignaciones:
            gid      = asig["grupo"].id
            mid      = asig["materia"].id
            lps      = asig["lec_per_session"]
            sesiones = asig["sesiones"]
            vlist    = gm_vars.get((gid, mid, lps), [])
            if vlist:
                self.modelo.Add(sum(vlist) == sesiones)
            else:
                logger.warning(
                    f"Sin variables: {asig['grupo'].nombre} – "
                    f"{asig['materia'].nombre} (lps={lps})"
                )

        # R3: pares gemelos — la misma materia de especialidad no puede solaparse
        # en día y lección entre los dos grupos del par (mismo tamaño de sesión).
        for (g1, g2) in self.pares_gemelos:
            # Índice rápido: (mid, lps, dia, l_ini) → var, para cada grupo
            idx_g1 = {
                (mid, lps, dia, l_ini): var
                for (gid, mid, lps, dia, l_ini), var in self.variables.items()
                if gid == g1.id
            }
            idx_g2 = {
                (mid, lps, dia, l_ini): var
                for (gid, mid, lps, dia, l_ini), var in self.variables.items()
                if gid == g2.id
            }

            count_r3 = 0
            for key, v1 in idx_g1.items():
                mid = key[0]
                mat = self.mat_cache.get(mid)
                if not mat or mat.especialidad_id is None:
                    continue
                v2 = idx_g2.get(key)
                if v2 is not None:
                    self.modelo.Add(v1 + v2 <= 1)
                    count_r3 += 1

            logger.info(
                f"R3 gemelos {g1.nombre}<->{g2.nombre}: {count_r3} restricciones"
            )

        logger.info("Restricciones aplicadas: R1 grupos | R2 cobertura | R3 gemelos")

    # ─────────────────────────────────────────────
    # PASO 3.5: OBJETIVO SUAVE — concentrar sesiones académicas
    # ─────────────────────────────────────────────
    def _agregar_objetivo_agrupamiento(self):
        """
        Minimiza el número de días distintos que usa cada (grupo, materia)
        para materias académicas (bps=1). Esto concentra sesiones en pocos
        días en lugar de dispersarlas de lunes a viernes.
        """
        penalizacion = []
        gm_dia_vars  = defaultdict(list)

        for (gid, mid, lps, dia, _), var in self.variables.items():
            # Solo sesiones pequeñas (1 o 2 lecciones = residuos de bps=1 o bps=2)
            # necesitan agrupamiento; las sesiones de bloque completo ya son compactas.
            if lps <= 2:
                gm_dia_vars[(gid, mid, dia)].append(var)

        for (gid, mid, dia), vars_dia in gm_dia_vars.items():
            dia_usado = self.modelo.NewBoolVar(f'dia_{gid}_{mid}_{dia}')
            self.modelo.AddMaxEquality(dia_usado, vars_dia)
            penalizacion.append(dia_usado)

        if penalizacion:
            self.modelo.Minimize(sum(penalizacion))
            logger.info(
                f"Objetivo: minimizar {len(penalizacion)} variables de día usado"
            )

    # ─────────────────────────────────────────────
    # PASO 3.7: DIAGNÓSTICO PRE-SOLVER
    # ─────────────────────────────────────────────
    def _verificar_viabilidad(self) -> list:
        problemas = []
        vars_por_gm = defaultdict(int)
        for key in self.variables:
            vars_por_gm[(key[0], key[1], key[2])] += 1

        for asig in self.asignaciones:
            gid  = asig["grupo"].id
            mid  = asig["materia"].id
            lps  = asig["lec_per_session"]
            req  = asig["sesiones"]
            disp = vars_por_gm[(gid, mid, lps)]
            if disp == 0:
                problemas.append(
                    f"SIN SLOTS: {asig['grupo'].nombre} – {asig['materia'].nombre} "
                    f"lps={lps} (requiere {req} sesion/es, 0 slots posibles)"
                )
            elif disp < req:
                problemas.append(
                    f"SLOTS INSUFICIENTES: {asig['grupo'].nombre} – "
                    f"{asig['materia'].nombre} lps={lps}: "
                    f"{disp} slots < {req} sesiones requeridas"
                )

        if problemas:
            logger.warning(
                f"⚠️  {len(problemas)} problema(s) detectado(s):\n  "
                + "\n  ".join(problemas)
            )
        else:
            logger.info("✅ Pre-solver: sin problemas obvios")

        return problemas

    # ─────────────────────────────────────────────
    # PASO 4: RESOLVER
    # ─────────────────────────────────────────────
    def _resolver(self) -> bool:
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 300.0
        solver.parameters.num_search_workers  = 8
        solver.parameters.log_search_progress = True

        logger.info("Resolviendo (máx 300s, 8 workers)...")
        estado = solver.Solve(self.modelo)
        nombre = solver.StatusName(estado)

        if estado in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            logger.info(f"✅ Solución encontrada: {nombre}")
            for clave, var in self.variables.items():
                if solver.Value(var) == 1:
                    self.resultado[clave] = True
            return True

        if estado == cp_model.INFEASIBLE:
            logger.error("❌ INFEASIBLE: no existe solución posible.")
        elif estado == cp_model.UNKNOWN:
            logger.error("⏱️  UNKNOWN: tiempo agotado sin encontrar solución.")
        else:
            logger.error(f"❌ Sin solución: {nombre}")

        return False

    # ─────────────────────────────────────────────
    # PASO 5: GUARDAR
    # ─────────────────────────────────────────────
    def _guardar_resultado(self) -> int:
        # Borrar horario generado anterior (conservar ediciones manuales)
        self.db.query(Horario)\
               .filter(Horario.anno_lectivo == self.anno_lectivo,
                       Horario.es_manual    == False)\
               .delete()

        count = 0
        for (gid, mid, lps, dia, l_ini) in self.resultado:
            l_fin  = l_ini + lps - 1
            bloque = LECCION_A_BLOQUE[l_ini]

            self.db.add(Horario(
                grupo_id       = gid,
                materia_id     = mid,
                dia            = dia,
                bloque         = bloque,
                leccion_inicio = l_ini,
                leccion_fin    = l_fin,
                anno_lectivo   = self.anno_lectivo,
                es_manual      = False,
            ))
            count += 1

        self.db.commit()
        logger.info(f"✅ {count} sesiones guardadas")
        return count

    # ─────────────────────────────────────────────
    # MÉTODO PRINCIPAL
    # ─────────────────────────────────────────────
    def generar(self) -> dict:
        try:
            logger.info(f"=== Generando horario {self.anno_lectivo} ===")
            self._cargar_datos()
            self._crear_variables()
            problemas = self._verificar_viabilidad()
            self._aplicar_restricciones()
            self._agregar_objetivo_agrupamiento()

            if not self._resolver():
                msg = "Sin solución."
                if problemas:
                    msg += "\nProblemas detectados:\n" + "\n".join(problemas[:10])
                return {"exito": False, "mensaje": msg, "lecciones_generadas": 0}

            count = self._guardar_resultado()
            return {
                "exito":               True,
                "mensaje":             "Horario generado correctamente",
                "lecciones_generadas": count,
                "anno_lectivo":        self.anno_lectivo,
            }

        except ValueError as e:
            self.db.rollback()
            return {"exito": False, "mensaje": str(e), "lecciones_generadas": 0}
        except Exception as e:
            logger.exception(f"Error inesperado: {e}")
            self.db.rollback()
            return {"exito": False, "mensaje": str(e), "lecciones_generadas": 0}
