import { useState, useEffect } from 'react'
import { Plus, Pencil, PowerOff } from 'lucide-react'
import api        from '../api/axios'
import Table      from '../components/Table'
import Modal      from '../components/Modal'
import PageHeader from '../components/PageHeader'
import FormField  from '../components/FormField'

const FORM_INICIAL = {
  nombre: '', nivel: 10, seccion: 'A',
  especialidad_ids: [], num_estudiantes: 30
}

export default function Grupos() {
  const [grupos,         setGrupos]         = useState([])
  const [especialidades, setEspecialidades] = useState([])
  const [loading,        setLoading]        = useState(true)
  const [modalForm,      setModalForm]      = useState(false)
  const [seleccionado,   setSeleccionado]   = useState(null)
  const [form,           setForm]           = useState(FORM_INICIAL)
  const [error,          setError]          = useState('')
  const [saving,         setSaving]         = useState(false)

  const cargar = async () => {
    setLoading(true)
    try {
      const [g, e] = await Promise.all([
        api.get('/grupos/'),
        api.get('/especialidades/')
      ])
      setGrupos(g.data)
      setEspecialidades(e.data)
    } finally { setLoading(false) }
  }

  useEffect(() => { cargar() }, [])

  const abrirForm = (grupo = null) => {
    setSeleccionado(grupo)
    setForm(grupo ? {
      nombre:           grupo.nombre,
      nivel:            grupo.nivel,
      seccion:          grupo.seccion,
      especialidad_ids: (grupo.especialidades ?? []).map(e => e.id),
      num_estudiantes:  grupo.num_estudiantes
    } : FORM_INICIAL)
    setError('')
    setModalForm(true)
  }

  const toggleEspecialidad = (id) => {
    setForm(prev => ({
      ...prev,
      especialidad_ids: prev.especialidad_ids.includes(id)
        ? prev.especialidad_ids.filter(e => e !== id)
        : [...prev.especialidad_ids, id]
    }))
  }

  const guardar = async () => {
    setSaving(true)
    setError('')
    try {
      if (seleccionado) {
        await api.put(`/grupos/${seleccionado.id}`, form)
      } else {
        await api.post('/grupos/', form)
      }
      setModalForm(false)
      cargar()
    } catch (e) {
      setError(e.response?.data?.detail ?? 'Error al guardar')
    } finally { setSaving(false) }
  }

  const desactivar = async (grupo) => {
    if (!confirm(`¿Desactivar el grupo "${grupo.nombre}"?`)) return
    try {
      await api.delete(`/grupos/${grupo.id}`)
      cargar()
    } catch {}
  }

  const columns = [
    { key: 'nombre',  label: 'Grupo' },
    { key: 'nivel',   label: 'Nivel',
      render: r => <span className="badge-verde">{r.nivel}°</span> },
    { key: 'seccion', label: 'Sección' },
    { key: 'especialidades', label: 'Especialidades',
      render: r => (r.especialidades ?? []).length > 0
        ? (r.especialidades ?? []).map(e => e.nombre).join(', ')
        : '—'
    },
    { key: 'num_estudiantes', label: 'Estudiantes',
      render: r => `${r.num_estudiantes} est.`
    },
    { key: 'activo', label: 'Estado',
      render: r => r.activo
        ? <span className="badge-verde">Activo</span>
        : <span className="badge-rojo">Inactivo</span>
    },
    { key: 'acciones', label: '',
      render: r => (
        <div className="flex items-center gap-2">
          <button onClick={() => abrirForm(r)}
                  className="p-1.5 rounded-lg hover:bg-verde-50 text-verde-600
                             transition-colors">
            <Pencil size={15} />
          </button>
          {r.activo && (
            <button onClick={() => desactivar(r)}
                    className="p-1.5 rounded-lg hover:bg-red-50 text-red-400
                               transition-colors">
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
        title="Grupos"
        subtitle="Secciones del colegio — 10°, 11° y 12°"
        action={
          <button onClick={() => abrirForm()}
                  className="btn-primary flex items-center gap-2">
            <Plus size={16} /> Nuevo Grupo
          </button>
        }
      />

      <div className="card">
        <Table columns={columns} data={grupos} loading={loading}
               emptyMessage="No hay grupos registrados" />
      </div>

      {/* Modal Grupo */}
      <Modal open={modalForm} onClose={() => setModalForm(false)}
             title={seleccionado ? 'Editar Grupo' : 'Nuevo Grupo'}>
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <FormField label="Nivel" required>
              <select className="input" value={form.nivel}
                      onChange={e => setForm({...form, nivel: +e.target.value})}>
                {[10,11,12].map(n => (
                  <option key={n} value={n}>{n}°</option>
                ))}
              </select>
            </FormField>
            <FormField label="Sección" required>
              <input className="input" value={form.seccion}
                     onChange={e => setForm({...form, seccion: e.target.value})}
                     placeholder="A" maxLength={5} />
            </FormField>
            <FormField label="Estudiantes" required>
              <input className="input" type="number" min={1} max={50}
                     value={form.num_estudiantes}
                     onChange={e => setForm({
                       ...form, num_estudiantes: +e.target.value
                     })} />
            </FormField>
          </div>

          <FormField label="Nombre del grupo" required>
            <input className="input" value={form.nombre}
                   onChange={e => setForm({...form, nombre: e.target.value})}
                   placeholder="10-A" />
          </FormField>

          <FormField label="Especialidades (puede seleccionar varias)">
            <div className="space-y-1.5 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-2">
              {especialidades.length === 0
                ? <p className="text-sm text-gray-400 px-1">No hay especialidades registradas</p>
                : especialidades.map(e => (
                  <label key={e.id}
                         className={`flex items-center gap-2.5 px-2 py-1.5 rounded-md
                                     cursor-pointer transition-colors
                                     ${form.especialidad_ids.includes(e.id)
                                       ? 'bg-verde-50 text-verde-700'
                                       : 'hover:bg-gray-50 text-gray-700'}`}>
                    <input type="checkbox"
                           checked={form.especialidad_ids.includes(e.id)}
                           onChange={() => toggleEspecialidad(e.id)}
                           className="accent-verde-500 flex-shrink-0" />
                    <span className="text-sm">{e.nombre}</span>
                  </label>
                ))
              }
            </div>
            {form.especialidad_ids.length > 0 && (
              <p className="text-xs text-verde-600 mt-1">
                {form.especialidad_ids.length} seleccionada(s)
              </p>
            )}
          </FormField>

          {error && (
            <p className="text-red-500 text-sm bg-red-50 px-3 py-2 rounded-lg">
              {error}
            </p>
          )}

          <div className="flex gap-3 pt-2">
            <button onClick={guardar} disabled={saving}
                    className="btn-primary flex-1 disabled:opacity-60">
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
            <button onClick={() => setModalForm(false)}
                    className="btn-secondary flex-1">
              Cancelar
            </button>
          </div>
        </div>
      </Modal>

    </div>
  )
}