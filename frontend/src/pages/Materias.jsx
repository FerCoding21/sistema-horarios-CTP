import { useState, useEffect } from 'react'
import { Plus, Pencil, PowerOff } from 'lucide-react'
import api from '../api/axios'
import Table from '../components/Table'
import Modal from '../components/Modal'
import PageHeader from '../components/PageHeader'
import FormField from '../components/FormField'

const DIAS    = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']
const TIPOS   = ['academica', 'tecnica']
const ESPACIOS = ['aula_regular', 'laboratorio', 'sala_computo', 'gimnasio', 'taller']
const NIVELES = [10, 11, 12]

const FORM_INICIAL = {
  nombre: '', codigo: '', tipo: 'academica',
  lecciones_semanales: 3,
  requiere_espacio: 'aula_regular',
  bloques_por_sesion: 3,
  niveles_aplicables: [10, 11, 12],
  especialidad_id: null,
  dias_permitidos: []
}

export default function Materias() {
  const [materias,       setMaterias]       = useState([])
  const [especialidades, setEspecialidades] = useState([])
  const [loading,        setLoading]        = useState(true)
  const [modalForm,      setModalForm]      = useState(false)
  const [seleccionado,   setSeleccionado]   = useState(null)
  const [form,   setForm]   = useState(FORM_INICIAL)
  const [error,  setError]  = useState('')
  const [saving, setSaving] = useState(false)

  const cargar = async () => {
    setLoading(true)
    try {
      const [m, e] = await Promise.all([
        api.get('/materias/'),
        api.get('/especialidades/')
      ])
      setMaterias(m.data)
      setEspecialidades(e.data)
    } finally { setLoading(false) }
  }

  useEffect(() => { cargar() }, [])

  const abrirForm = (mat = null) => {
    setSeleccionado(mat)
    setForm(mat ? {
      nombre:              mat.nombre,
      codigo:              mat.codigo,
      tipo:                mat.tipo,
      lecciones_semanales: mat.lecciones_semanales,
      requiere_espacio:    mat.requiere_espacio,
      bloques_por_sesion:  mat.bloques_por_sesion ?? 3,
      niveles_aplicables:  mat.niveles_aplicables ?? [10, 11, 12],
      especialidad_id:     mat.especialidad_id ?? null,
      dias_permitidos:     mat.dias_permitidos ?? []
    } : FORM_INICIAL)
    setError('')
    setModalForm(true)
  }

  const toggleNivel = (n) => {
    setForm(prev => ({
      ...prev,
      niveles_aplicables: prev.niveles_aplicables.includes(n)
        ? prev.niveles_aplicables.filter(x => x !== n)
        : [...prev.niveles_aplicables, n].sort()
    }))
  }

  const toggleDia = (dia) => {
    setForm(prev => ({
      ...prev,
      dias_permitidos: prev.dias_permitidos.includes(dia)
        ? prev.dias_permitidos.filter(d => d !== dia)
        : [...prev.dias_permitidos, dia]
    }))
  }

  const guardar = async () => {
    if (form.niveles_aplicables.length === 0) {
      setError('Selecciona al menos un nivel')
      return
    }
    setSaving(true)
    setError('')
    try {
      if (seleccionado) {
        await api.put(`/materias/${seleccionado.id}`, form)
      } else {
        await api.post('/materias/', form)
      }
      setModalForm(false)
      cargar()
    } catch (e) {
      setError(e.response?.data?.detail ?? 'Error al guardar')
    } finally { setSaving(false) }
  }

  const desactivar = async (mat) => {
    if (!confirm(`¿Desactivar la materia "${mat.nombre}"?`)) return
    try { await api.delete(`/materias/${mat.id}`); cargar() } catch {}
  }

  const labelNiveles = (niveles) => {
    if (!niveles || niveles.length === 3) return <span className="text-xs text-gray-400">Todos</span>
    return niveles.map(n => (
      <span key={n} className="badge-amarillo mr-1">{n}°</span>
    ))
  }

  const nombreEspecialidad = (id) =>
    especialidades.find(e => e.id === id)?.nombre ?? '—'

  const columns = [
    { key: 'codigo', label: 'Código' },
    { key: 'nombre', label: 'Materia' },
    { key: 'tipo', label: 'Tipo',
      render: r => (
        <span className={r.tipo === 'tecnica' ? 'badge-amarillo' : 'badge-verde'}>
          {r.tipo}
        </span>
      )
    },
    { key: 'especialidad_id', label: 'Especialidad',
      render: r => r.especialidad_id
        ? <span className="text-xs text-gray-600">{nombreEspecialidad(r.especialidad_id)}</span>
        : <span className="text-xs text-gray-400">Académica</span>
    },
    { key: 'niveles_aplicables', label: 'Niveles',
      render: r => labelNiveles(r.niveles_aplicables)
    },
    { key: 'lecciones_semanales', label: 'Lec/sem',
      render: r => <span className="badge-verde">{r.lecciones_semanales}</span>
    },
    { key: 'bloques_por_sesion', label: 'Por sesión',
      render: r => {
        const n = r.bloques_por_sesion / 3
        return <span className="text-xs text-gray-500">{n} bloque{n !== 1 ? 's' : ''} ({r.bloques_por_sesion} lec)</span>
      }
    },
    { key: 'requiere_espacio', label: 'Espacio',
      render: r => (
        <span className="text-xs text-gray-500 capitalize">
          {r.requiere_espacio.replace(/_/g, ' ')}
        </span>
      )
    },
    { key: 'dias_permitidos', label: 'Días',
      render: r => r.dias_permitidos?.length > 0
        ? <span className="text-xs text-amarillo-600 capitalize">
            {r.dias_permitidos.join(', ')}
          </span>
        : <span className="text-xs text-gray-400">Todos</span>
    },
    { key: 'activo', label: 'Estado',
      render: r => r.activo
        ? <span className="badge-verde">Activa</span>
        : <span className="text-xs text-red-400">Inactiva</span>
    },
    { key: 'acciones', label: '',
      render: r => (
        <div className="flex items-center gap-2">
          <button onClick={() => abrirForm(r)}
            className="p-1.5 rounded-lg hover:bg-verde-50 text-verde-600 transition-colors">
            <Pencil size={15} />
          </button>
          {r.activo && (
            <button onClick={() => desactivar(r)}
              className="p-1.5 rounded-lg hover:bg-red-50 text-red-400 transition-colors">
              <PowerOff size={15} />
            </button>
          )}
        </div>
      )
    }
  ]

  return (
    <div className="fade-in">
      <PageHeader
        title="Materias"
        subtitle="Gestión de asignaturas del plan de estudios"
        action={
          <button onClick={() => abrirForm()}
            className="btn-primary flex items-center gap-2">
            <Plus size={16} /> Nueva Materia
          </button>
        }
      />

      <div className="card">
        <Table columns={columns} data={materias} loading={loading}
          emptyMessage="No hay materias registradas" />
      </div>

      <Modal open={modalForm} onClose={() => setModalForm(false)}
        title={seleccionado ? 'Editar Materia' : 'Nueva Materia'}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Nombre" required>
              <input className="input" value={form.nombre}
                onChange={e => setForm({ ...form, nombre: e.target.value })}
                placeholder="Matemática" />
            </FormField>
            <FormField label="Código" required>
              <input className="input" value={form.codigo}
                onChange={e => setForm({ ...form, codigo: e.target.value.toUpperCase() })}
                placeholder="MAT" disabled={!!seleccionado} />
            </FormField>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <FormField label="Tipo" required>
              <select className="input" value={form.tipo}
                onChange={e => setForm({
                  ...form,
                  tipo: e.target.value,
                  especialidad_id: e.target.value === 'academica' ? null : form.especialidad_id
                })}>
                {TIPOS.map(t => (
                  <option key={t} value={t} className="capitalize">{t}</option>
                ))}
              </select>
            </FormField>
            <FormField label="Lecciones / semana" required>
              <input className="input" type="number" min={1} max={40}
                value={form.lecciones_semanales}
                onChange={e => setForm({ ...form, lecciones_semanales: +e.target.value })} />
            </FormField>
          </div>

          {form.tipo === 'tecnica' && (
            <FormField label="Especialidad" required>
              <select className="input" value={form.especialidad_id ?? ''}
                onChange={e => setForm({
                  ...form,
                  especialidad_id: e.target.value ? +e.target.value : null
                })}>
                <option value="">— Seleccionar especialidad —</option>
                {especialidades.map(e => (
                  <option key={e.id} value={e.id}>{e.nombre}</option>
                ))}
              </select>
              {!form.especialidad_id && (
                <p className="text-xs text-amber-500 mt-1">
                  Las materias técnicas deben pertenecer a una especialidad
                </p>
              )}
            </FormField>
          )}

          <div className="grid grid-cols-2 gap-4">
            <FormField label="Espacio requerido" required>
              <select className="input" value={form.requiere_espacio}
                onChange={e => setForm({ ...form, requiere_espacio: e.target.value })}>
                {ESPACIOS.map(e => (
                  <option key={e} value={e}>{e.replace(/_/g, ' ')}</option>
                ))}
              </select>
            </FormField>
            <FormField label="Bloques por sesión" required>
              <select className="input" value={form.bloques_por_sesion}
                onChange={e => setForm({ ...form, bloques_por_sesion: +e.target.value })}>
                <option value={3}>1 bloque — 3 lecciones (120 min)</option>
                <option value={6}>2 bloques — 6 lecciones (medio día)</option>
                <option value={9}>3 bloques — 9 lecciones</option>
                <option value={12}>4 bloques — 12 lecciones (día completo)</option>
              </select>
            </FormField>
          </div>

          {/* Niveles con checkboxes */}
          <FormField label="Niveles en que se imparte" required>
            <div className="flex gap-3 mt-1">
              {NIVELES.map(n => (
                <label key={n}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border cursor-pointer
                              transition-all font-medium text-sm
                              ${form.niveles_aplicables.includes(n)
                                ? 'bg-verde-500 text-white border-verde-500'
                                : 'bg-white text-gray-600 border-gray-200 hover:border-verde-300'}`}>
                  <input type="checkbox" className="hidden"
                    checked={form.niveles_aplicables.includes(n)}
                    onChange={() => toggleNivel(n)} />
                  {n}°
                </label>
              ))}
            </div>
            {form.niveles_aplicables.length === 0 && (
              <p className="text-xs text-red-500 mt-1">Selecciona al menos un nivel</p>
            )}
          </FormField>

          {/* Días permitidos */}
          <FormField label="Días permitidos (vacío = todos los días)">
            <div className="flex flex-wrap gap-2 mt-1">
              {DIAS.map(dia => (
                <button key={dia} type="button"
                  onClick={() => toggleDia(dia)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-all capitalize
                              ${form.dias_permitidos.includes(dia)
                                ? 'bg-verde-500 text-white border-verde-500'
                                : 'bg-white text-gray-600 border-gray-200 hover:border-verde-300'}`}>
                  {dia}
                </button>
              ))}
            </div>
          </FormField>

          {error && (
            <p className="text-red-500 text-sm bg-red-50 px-3 py-2 rounded-lg">{error}</p>
          )}

          <div className="flex gap-3 pt-2">
            <button onClick={guardar} disabled={saving}
              className="btn-primary flex-1 disabled:opacity-60">
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
            <button onClick={() => setModalForm(false)} className="btn-secondary flex-1">
              Cancelar
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
