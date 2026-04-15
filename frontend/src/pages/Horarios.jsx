import { useState, useEffect } from 'react'
import { Calendar, Play, RefreshCw, FileText, FileSpreadsheet } from 'lucide-react'
import api        from '../api/axios'
import PageHeader from '../components/PageHeader'
import Modal      from '../components/Modal'
import FormField  from '../components/FormField'
import { exportarPDF, exportarExcel } from '../utils/exportHorario'

const DIAS = ['lunes','martes','miercoles','jueves','viernes']
const DIAS_LABEL = {
  lunes:'Lunes', martes:'Martes', miercoles:'Miércoles',
  jueves:'Jueves', viernes:'Viernes'
}

const BLOQUES = [
  { bloque: 1, lecciones: [1,2,3],    hora: '7:00 – 9:00',   label: 'A' },
  { bloque: 2, lecciones: [4,5,6],    hora: '9:20 – 11:20',  label: 'B' },
  { bloque: 3, lecciones: [7,8,9],    hora: '12:00 – 2:00',  label: 'C' },
  { bloque: 4, lecciones: [10,11,12], hora: '2:20 – 4:20',   label: 'D' },
]

const LECCIONES_DETALLE = [
  { num: 1,  hora: '7:00 - 7:40'   }, { num: 2,  hora: '7:40 - 8:20'   },
  { num: 3,  hora: '8:20 - 9:00'   },
  { num: 4,  hora: '9:20 - 10:00'  }, { num: 5,  hora: '10:00 - 10:40' },
  { num: 6,  hora: '10:40 - 11:20' },
  { num: 7,  hora: '12:00 - 12:40' }, { num: 8,  hora: '12:40 - 1:20'  },
  { num: 9,  hora: '1:20 - 2:00'   },
  { num: 10, hora: '2:20 - 3:00'   }, { num: 11, hora: '3:00 - 3:40'   },
  { num: 12, hora: '3:40 - 4:20'   },
]

const COLORES = [
  'bg-verde-100 text-verde-800 border-verde-300',
  'bg-blue-100 text-blue-800 border-blue-300',
  'bg-purple-100 text-purple-800 border-purple-300',
  'bg-orange-100 text-orange-800 border-orange-300',
  'bg-pink-100 text-pink-800 border-pink-300',
  'bg-teal-100 text-teal-800 border-teal-300',
  'bg-yellow-100 text-yellow-800 border-yellow-300',
  'bg-indigo-100 text-indigo-800 border-indigo-300',
  'bg-rose-100 text-rose-800 border-rose-300',
  'bg-cyan-100 text-cyan-800 border-cyan-300',
]

const SEPARADORES = [
  { despues_de: 3, label: 'Recreo   9:00 – 9:20',   color: 'bg-gray-100' },
  { despues_de: 6, label: 'Almuerzo 11:20 – 12:00', color: 'bg-amber-50' },
  { despues_de: 9, label: 'Recreo   2:00 – 2:20',   color: 'bg-gray-100' },
]

export default function Horarios() {
  const [grupos,      setGrupos]      = useState([])
  const [horario,     setHorario]     = useState([])
  const [loading,     setLoading]     = useState(false)
  const [generando,   setGenerando]   = useState(false)
  const [grupoId,     setGrupoId]     = useState('')
  const [annoLectivo, setAnnoLectivo] = useState(2026)
  const [resultado,   setResultado]   = useState(null)
  const [colorMap,    setColorMap]    = useState({})
  const [trackId,     setTrackId]     = useState(null)   // null = todas (grupos 1-esp)
  const [modalEdit,   setModalEdit]   = useState(false)
  const [leccionEdit, setLeccionEdit] = useState(null)
  const [editForm,    setEditForm]    = useState({})
  const [saving,      setSaving]      = useState(false)

  useEffect(() => {
    api.get('/grupos/').then(r => setGrupos(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    // Asignar colores a todas las materias del horario completo
    // (no solo las filtradas, para que los colores sean consistentes al cambiar pista)
    const materias = [...new Set(horario.map(l => l.materia))]
    const mapa = {}
    materias.forEach((m, i) => { mapa[m] = COLORES[i % COLORES.length] })
    setColorMap(mapa)
  }, [horario])

  // Cuando cambia el grupo, resetear la pista al primer track disponible
  useEffect(() => {
    const g = grupos.find(g => g.id === +grupoId)
    const esps = g?.especialidades ?? []
    setTrackId(esps.length > 1 ? esps[0].id : null)
  }, [grupoId, grupos])

  useEffect(() => {
    if (grupoId) cargarHorario()
  }, [grupoId, annoLectivo])

  const cargarHorario = async () => {
    if (!grupoId) return
    setLoading(true)
    try {
      const res = await api.get(`/horarios/grupo/${grupoId}?anno_lectivo=${annoLectivo}`)
      setHorario(res.data)
    } catch { setHorario([]) }
    finally  { setLoading(false) }
  }

  const generarHorario = async () => {
    if (!confirm(`¿Generar horario ${annoLectivo}? Esto reemplazará el horario automático existente.`)) return
    setGenerando(true)
    setResultado(null)
    try {
      const res = await api.post(`/horarios/generar?anno_lectivo=${annoLectivo}`)
      setResultado(res.data)
      if (res.data.exito && grupoId) cargarHorario()
    } catch (e) {
      setResultado({ exito: false, mensaje: e.response?.data?.detail ?? 'Error' })
    } finally { setGenerando(false) }
  }

  // Horario filtrado según pista seleccionada:
  // - grupos multi-especialidad: solo sesiones de la pista activa + académicas compartidas
  // - grupos de una especialidad: todo visible
  const horarioFiltrado = horario.filter(s =>
    trackId === null ||
    s.especialidad_id === null ||
    s.especialidad_id === trackId
  )

  const getSesion = (dia, numLeccion) =>
    horarioFiltrado.find(l =>
      l.dia === dia &&
      l.leccion_inicio <= numLeccion &&
      l.leccion_fin    >= numLeccion
    )

  const esPrimeraLeccion = (dia, numLeccion) => {
    const s = getSesion(dia, numLeccion)
    return s ? s.leccion_inicio === numLeccion : false
  }

  const rowSpan = (dia, numLeccion) => {
    const s = getSesion(dia, numLeccion)
    if (!s) return 1
    // Filas de lección que ocupa la sesión
    const base = s.leccion_fin - s.leccion_inicio + 1
    // Filas de separador que caen DENTRO del rango de la sesión
    // (un separador "despues_de: X" está entre la fila X y la fila X+1,
    //  así que cae dentro si l_ini <= X < l_fin)
    const extras = SEPARADORES.filter(
      sep => s.leccion_inicio <= sep.despues_de && sep.despues_de < s.leccion_fin
    ).length
    return base + extras
  }

  // ¿Una sesión activa en (dia) sigue "viva" al llegar al separador despues_de?
  const sesionSpanSepar = (dia, despues_de) =>
    horarioFiltrado.some(l =>
      l.dia             === dia &&
      l.leccion_inicio  <= despues_de &&
      l.leccion_fin     >  despues_de
    )

  const abrirEditar = (sesion) => {
    setLeccionEdit(sesion)
    setEditForm({ dia: sesion.dia, bloque: sesion.bloque })
    setModalEdit(true)
  }

  const guardarEdicion = async () => {
    setSaving(true)
    try {
      await api.patch(`/horarios/leccion/${leccionEdit.id}`, editForm)
      setModalEdit(false)
      cargarHorario()
    } catch (e) {
      alert(e.response?.data?.detail ?? 'Conflicto — no se puede mover')
    } finally { setSaving(false) }
  }

  const nombreGrupo = () =>
    grupos.find(g => g.id === +grupoId)?.nombre ?? ''

  return (
    <div className="fade-in">
      <PageHeader
        title="Horarios"
        subtitle="Generación y visualización de horarios académicos"
      />

      {/* ── Panel de control ── */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="label">Año Lectivo</label>
            <input type="number" className="input w-28"
                   value={annoLectivo}
                   onChange={e => setAnnoLectivo(+e.target.value)} />
          </div>

          <div className="flex-1 min-w-48">
            <label className="label">Grupo</label>
            <select className="input" value={grupoId}
                    onChange={e => setGrupoId(e.target.value)}>
              <option value="">Seleccionar grupo...</option>
              {grupos.map(g => (
                <option key={g.id} value={g.id}>{g.nombre}</option>
              ))}
            </select>
          </div>

          {/* Selector de pista — solo para grupos con 2 especialidades */}
          {grupoId && (() => {
            const g    = grupos.find(x => x.id === +grupoId)
            const esps = g?.especialidades ?? []
            if (esps.length < 2) return null
            return (
              <div>
                <label className="label">Especialidad</label>
                <div className="flex gap-1.5">
                  {esps.map(e => (
                    <button key={e.id}
                            onClick={() => setTrackId(e.id)}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium
                                        border transition-colors
                                        ${trackId === e.id
                                          ? 'bg-verde-500 text-white border-verde-500'
                                          : 'bg-white text-gray-600 border-gray-200 hover:border-verde-300'}`}>
                      {e.nombre}
                    </button>
                  ))}
                </div>
              </div>
            )
          })()}

          {grupoId && (
            <button onClick={cargarHorario}
                    className="btn-secondary flex items-center gap-2">
              <RefreshCw size={15} /> Actualizar
            </button>
          )}

          <div className="flex-1" />

          <button onClick={generarHorario} disabled={generando}
                  className="btn-primary flex items-center gap-2
                             disabled:opacity-60 disabled:cursor-not-allowed">
            {generando
              ? <><RefreshCw size={15} className="animate-spin" /> Generando...</>
              : <><Play size={15} /> Generar Horario {annoLectivo}</>
            }
          </button>
        </div>

        {resultado && (
          <div className={`mt-4 px-4 py-3 rounded-lg border fade-in
                           ${resultado.exito
                             ? 'bg-verde-50 border-verde-200 text-verde-700'
                             : 'bg-red-50 border-red-200 text-red-600'}`}>
            <p className="font-medium">
              {resultado.exito ? '✅' : '❌'} {resultado.mensaje}
            </p>
            {resultado.exito && (
              <p className="text-sm mt-0.5 opacity-80">
                {resultado.lecciones_generadas} sesiones generadas
              </p>
            )}
          </div>
        )}
      </div>

      {/* ── Grilla del horario ── */}
      {!grupoId ? (
        <div className="card flex flex-col items-center justify-center py-16">
          <Calendar size={48} className="text-verde-200 mb-4" />
          <p className="text-gray-400 text-lg font-medium">
            Seleccioná un grupo para ver su horario
          </p>
          <p className="text-gray-300 text-sm mt-1">
            O generá el horario automático con el botón verde
          </p>
        </div>
      ) : loading ? (
        <div className="card flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 border-verde-200 border-t-verde-500
                          rounded-full animate-spin" />
        </div>
      ) : (
        <div className="card overflow-x-auto fade-in">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="font-display text-lg font-bold text-verde-700">
                Grupo: {nombreGrupo()}
              </h2>
              <p className="text-gray-400 text-sm">
                {(() => {
                  const g    = grupos.find(x => x.id === +grupoId)
                  const esps = g?.especialidades ?? []
                  const esp  = esps.find(e => e.id === trackId)
                  const pista = esp ? ` · ${esp.nombre}` : ''
                  return `Año lectivo ${annoLectivo}${pista} · ${horarioFiltrado.length} sesiones`
                })()}
              </p>
            </div>

            <div className="flex items-center gap-3">
              {horarioFiltrado.length > 0 && (
                <div className="flex flex-wrap gap-1.5 max-w-xs justify-end">
                  {[...new Set(horarioFiltrado.map(s => s.materia))].map(materia => (
                    <span key={materia}
                          className={`text-xs px-2 py-0.5 rounded-full border
                                      ${colorMap[materia] ?? COLORES[0]}`}>
                      {materia.length > 20 ? materia.slice(0, 20) + '…' : materia}
                    </span>
                  ))}
                </div>
              )}

              {horarioFiltrado.length > 0 && (() => {
                const g   = grupos.find(x => x.id === +grupoId)
                const esp = g?.especialidades?.find(e => e.id === trackId)?.nombre ?? ''
                return (
                  <div className="flex gap-2 shrink-0">
                    <button
                      onClick={() => exportarPDF(horarioFiltrado, nombreGrupo(), annoLectivo, esp)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium
                                 rounded-lg border border-red-200 text-red-600
                                 hover:bg-red-50 transition-colors">
                      <FileText size={14} /> PDF
                    </button>
                    <button
                      onClick={() => exportarExcel(horarioFiltrado, nombreGrupo(), annoLectivo, esp)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium
                                 rounded-lg border border-green-200 text-green-700
                                 hover:bg-green-50 transition-colors">
                      <FileSpreadsheet size={14} /> Excel
                    </button>
                  </div>
                )
              })()}
            </div>
          </div>

          {horarioFiltrado.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <p>No hay horario generado para este grupo.</p>
              <p className="text-sm mt-1">Usá el botón "Generar Horario".</p>
            </div>
          ) : (
            <table className="w-full text-xs border-collapse min-w-[750px]">
              <thead>
                <tr>
                  <th className="table-header px-2 py-2.5 text-center w-10
                                 rounded-tl-xl border-r border-verde-500">
                    Lecc.
                  </th>
                  <th className="table-header px-2 py-2.5 text-center w-28
                                 border-r border-verde-500">
                    Hora
                  </th>
                  {DIAS.map((dia, i) => (
                    <th key={dia}
                        className={`table-header px-2 py-2.5 text-center
                                    ${i === DIAS.length - 1 ? 'rounded-tr-xl' : ''}`}>
                      {DIAS_LABEL[dia]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {LECCIONES_DETALLE.map(({ num, hora }) => {
                  const separador = SEPARADORES.find(s => s.despues_de === num - 1)
                  return (
                    <>
                      {separador && (
                        <tr key={`sep-${num}`}>
                          {/* Solo span las 2 columnas de encabezado (Lecc + Hora).
                              Las columnas de días NO reciben <td> si una sesión activa
                              ya tiene un rowspan que las cubre — así el rowspan puede
                              cruzar esta fila sin conflicto. */}
                          <td colSpan={2}
                              className={`${separador.color} text-center py-1
                                          text-xs font-medium text-gray-500
                                          border-y border-gray-200`}>
                            {separador.label}
                          </td>
                          {DIAS.map(dia =>
                            sesionSpanSepar(dia, separador.despues_de) ? null : (
                              <td key={dia}
                                  className={`${separador.color} border-y border-gray-200`} />
                            )
                          )}
                        </tr>
                      )}
                      <tr key={num} className="border-b border-gray-100 hover:bg-gray-50/50">
                        <td className="px-2 py-1 text-center font-bold
                                       text-verde-700 border-r border-gray-100 w-10">
                          {num}
                        </td>
                        <td className="px-2 py-1 text-center text-gray-500
                                       border-r border-gray-100 w-28 whitespace-nowrap">
                          {hora}
                        </td>
                        {DIAS.map(dia => {
                          const sesion = getSesion(dia, num)
                          if (sesion && !esPrimeraLeccion(dia, num)) return null
                          const span = sesion ? rowSpan(dia, num) : 1
                          return (
                            <td key={dia} rowSpan={span}
                                className="relative p-0 border-l border-gray-100">
                              {sesion ? (
                                <button
                                  onClick={() => abrirEditar(sesion)}
                                  className={`absolute inset-[3px] text-left px-2 py-1
                                              rounded-lg border transition-all
                                              hover:shadow-md hover:scale-[1.01]
                                              active:scale-[0.99]
                                              flex flex-col justify-center
                                              ${colorMap[sesion.materia] ?? COLORES[0]}
                                              ${sesion.es_manual ? 'ring-1 ring-amarillo-400' : ''}`}>
                                  <p className="font-semibold leading-tight">
                                    {sesion.materia}
                                  </p>
                                  {sesion.es_manual && (
                                    <span className="text-amarillo-500 text-xs">✏️ manual</span>
                                  )}
                                </button>
                              ) : (
                                <div className="absolute inset-[3px] rounded border border-dashed
                                                border-gray-200 bg-gray-50/30" />
                              )}
                            </td>
                          )
                        })}
                      </tr>
                    </>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* ── Modal editar ── */}
      <Modal open={modalEdit} onClose={() => setModalEdit(false)}
             title="Mover sesión" size="sm">
        {leccionEdit && (
          <div className="space-y-4">
            <div className={`px-4 py-3 rounded-lg border
                             ${colorMap[leccionEdit.materia] ?? COLORES[0]}`}>
              <p className="font-bold">{leccionEdit.materia}</p>
              <p className="text-xs opacity-60 mt-0.5">
                Lecciones {leccionEdit.leccion_inicio}–{leccionEdit.leccion_fin}
                {' · '}{DIAS_LABEL[leccionEdit.dia]}
              </p>
            </div>

            <FormField label="Día">
              <select className="input" value={editForm.dia}
                      onChange={e => setEditForm({ ...editForm, dia: e.target.value })}>
                {DIAS.map(d => (
                  <option key={d} value={d}>{DIAS_LABEL[d]}</option>
                ))}
              </select>
            </FormField>

            <FormField label="Bloque">
              <select className="input" value={editForm.bloque}
                      onChange={e => setEditForm({ ...editForm, bloque: +e.target.value })}>
                {BLOQUES.map(b => (
                  <option key={b.bloque} value={b.bloque}>
                    Bloque {b.label} — {b.hora}
                  </option>
                ))}
              </select>
            </FormField>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-2.5">
              <p className="text-yellow-700 text-xs">
                ⚠️ El sistema verificará conflictos antes de guardar.
              </p>
            </div>

            <div className="flex gap-3">
              <button onClick={guardarEdicion} disabled={saving}
                      className="btn-primary flex-1 disabled:opacity-60">
                {saving ? 'Verificando...' : 'Guardar cambio'}
              </button>
              <button onClick={() => setModalEdit(false)}
                      className="btn-secondary flex-1">
                Cancelar
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
