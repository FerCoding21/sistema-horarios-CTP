import { useState, useEffect } from 'react'
import { Plus, Pencil, PowerOff, BookOpen } from 'lucide-react'
import api        from '../api/axios'
import Table      from '../components/Table'
import Modal      from '../components/Modal'
import PageHeader from '../components/PageHeader'
import FormField  from '../components/FormField'

const FORM_INICIAL = { nombre: '', codigo: '' }

const TIPO_HORARIO_OPTS = [
  { value: 'general',  label: 'General (sin restricción de días)' },
  { value: 'split_10', label: 'Split 10° — Técnicas Lun+Mar+Mié-AM · Generales Mié-PM+Jue+Vie' },
  { value: 'split_11', label: 'Split 11° — Técnicas Lun+Mar · Generales Mié+Jue+Vie' },
  { value: 'split_12', label: 'Split 12° — Técnicas Lun+Mar · Generales Mié+Jue+Vie' },
]

const TIPO_LABEL = {
  general:  'General',
  split_10: 'Split 10°',
  split_11: 'Split 11°',
  split_12: 'Split 12°',
}

export default function Especialidades() {
  const [especialidades, setEspecialidades] = useState([])
  const [grupos,         setGrupos]         = useState([])
  const [loading,        setLoading]        = useState(true)
  const [modalForm,      setModalForm]      = useState(false)
  const [modalGrupos,    setModalGrupos]    = useState(false)
  const [seleccionada,   setSeleccionada]   = useState(null)
  const [grupoEdit,      setGrupoEdit]      = useState(null)
  const [form,           setForm]           = useState(FORM_INICIAL)
  const [tipoHorario,    setTipoHorario]    = useState('general')
  const [error,          setError]          = useState('')
  const [saving,         setSaving]         = useState(false)

  const cargar = async () => {
    setLoading(true)
    try {
      const [e, g] = await Promise.all([
        api.get('/especialidades/'),
        api.get('/grupos/'),
      ])
      setEspecialidades(e.data)
      setGrupos(g.data)
    } finally { setLoading(false) }
  }

  useEffect(() => { cargar() }, [])

  /* ── Especialidad CRUD ── */
  const abrirForm = (esp = null) => {
    setSeleccionada(esp)
    setForm(esp ? { nombre: esp.nombre, codigo: esp.codigo } : FORM_INICIAL)
    setError('')
    setModalForm(true)
  }

  const guardar = async () => {
    setSaving(true); setError('')
    try {
      if (seleccionada)
        await api.put(`/especialidades/${seleccionada.id}`, form)
      else
        await api.post('/especialidades/', form)
      setModalForm(false)
      cargar()
    } catch (e) {
      setError(e.response?.data?.detail ?? 'Error al guardar')
    } finally { setSaving(false) }
  }

  const desactivar = async (esp) => {
    if (!confirm(`¿Desactivar la especialidad "${esp.nombre}"?`)) return
    try { await api.delete(`/especialidades/${esp.id}`); cargar() } catch {}
  }

  /* ── Tipo horario de grupo ── */
  const abrirTipoHorario = (grupo) => {
    setGrupoEdit(grupo)
    setTipoHorario(grupo.tipo_horario ?? 'general')
    setModalGrupos(true)
  }

  const guardarTipoHorario = async () => {
    setSaving(true)
    try {
      await api.put(`/grupos/${grupoEdit.id}`, { tipo_horario: tipoHorario })
      setModalGrupos(false)
      cargar()
    } catch (e) {
      alert(e.response?.data?.detail ?? 'Error al guardar')
    } finally { setSaving(false) }
  }

  /* ── Columnas ── */
  const colsEsp = [
    { key: 'codigo', label: 'Código' },
    { key: 'nombre', label: 'Nombre' },
    {
      key: '_grupos', label: 'Grupos',
      render: (esp) => {
        const n = grupos.filter(g =>
          g.especialidades?.some(e => e.id === esp.id)
        ).length
        return <span className="text-gray-500">{n} grupo{n !== 1 ? 's' : ''}</span>
      }
    },
    {
      key: 'activo', label: 'Estado',
      render: (esp) => (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium
          ${esp.activo ? 'bg-verde-100 text-verde-700' : 'bg-gray-100 text-gray-500'}`}>
          {esp.activo ? 'Activa' : 'Inactiva'}
        </span>
      )
    },
    {
      key: 'acciones', label: '',
      render: (esp) => (
        <div className="flex gap-2">
          <button onClick={() => abrirForm(esp)}
            className="p-1.5 text-gray-400 hover:text-verde-600 hover:bg-verde-50 rounded-lg transition-colors">
            <Pencil size={14} />
          </button>
          {esp.activo && (
            <button onClick={() => desactivar(esp)}
              className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
              <PowerOff size={14} />
            </button>
          )}
        </div>
      )
    },
  ]

  const colsGrupos = [
    { key: 'nombre', label: 'Grupo' },
    { key: 'nivel',  label: 'Nivel', render: (g) => `${g.nivel}°` },
    {
      key: '_especialidades', label: 'Especialidades',
      render: (g) => (
        <span className="text-gray-600 text-xs">
          {g.especialidades?.map(e => e.nombre).join(' / ') || '—'}
        </span>
      )
    },
    {
      key: 'tipo_horario', label: 'Tipo de horario',
      render: (g) => (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium
          ${g.tipo_horario === 'general'
            ? 'bg-gray-100 text-gray-600'
            : 'bg-blue-100 text-blue-700'}`}>
          {TIPO_LABEL[g.tipo_horario] ?? g.tipo_horario}
        </span>
      )
    },
    {
      key: 'acciones', label: '',
      render: (grupo) => (
        <button onClick={() => abrirTipoHorario(grupo)}
          className="p-1.5 text-gray-400 hover:text-verde-600 hover:bg-verde-50 rounded-lg transition-colors"
          title="Cambiar tipo de horario">
          <Pencil size={14} />
        </button>
      )
    },
  ]

  return (
    <div className="fade-in">
      <PageHeader
        title="Especialidades"
        subtitle="Gestión de especialidades técnicas y configuración de horarios por grupo"
      />

      {/* ── Especialidades ── */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display font-bold text-verde-700">Especialidades</h2>
          <button onClick={() => abrirForm()}
                  className="btn-primary flex items-center gap-2">
            <Plus size={15} /> Nueva especialidad
          </button>
        </div>

        <Table
          columns={colsEsp}
          data={especialidades}
          loading={loading}
          emptyMessage="No hay especialidades registradas"
        />
      </div>

      {/* ── Tipo de horario por grupo ── */}
      <div className="card">
        <div className="flex items-center gap-2 mb-1">
          <BookOpen size={18} className="text-verde-500" />
          <h2 className="font-display font-bold text-verde-700">
            Tipo de horario por grupo
          </h2>
        </div>
        <p className="text-sm text-gray-400 mb-4">
          Configurá si el grupo tiene división de días entre materias técnicas y generales.
        </p>

        <Table
          columns={colsGrupos}
          data={grupos}
          loading={loading}
          emptyMessage="No hay grupos registrados"
        />
      </div>

      {/* ── Modal especialidad ── */}
      <Modal open={modalForm} onClose={() => setModalForm(false)}
             title={seleccionada ? 'Editar especialidad' : 'Nueva especialidad'}
             size="sm">
        <div className="space-y-4">
          <FormField label="Nombre">
            <input className="input" value={form.nombre}
                   onChange={e => setForm({ ...form, nombre: e.target.value })}
                   placeholder="Ej: Mecánica de Precisión" />
          </FormField>
          <FormField label="Código">
            <input className="input" value={form.codigo}
                   onChange={e => setForm({ ...form, codigo: e.target.value.toUpperCase() })}
                   placeholder="Ej: MP" maxLength={10} />
          </FormField>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <div className="flex gap-3">
            <button onClick={guardar} disabled={saving}
                    className="btn-primary flex-1 disabled:opacity-60">
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
            <button onClick={() => setModalForm(false)}
                    className="btn-secondary flex-1">Cancelar</button>
          </div>
        </div>
      </Modal>

      {/* ── Modal tipo horario ── */}
      <Modal open={modalGrupos} onClose={() => setModalGrupos(false)}
             title={`Tipo de horario — ${grupoEdit?.nombre}`}
             size="sm">
        <div className="space-y-4">
          <FormField label="Patrón de días">
            <select className="input" value={tipoHorario}
                    onChange={e => setTipoHorario(e.target.value)}>
              {TIPO_HORARIO_OPTS.map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </FormField>

          {tipoHorario !== 'general' && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2.5 text-xs text-blue-700 space-y-1">
              {tipoHorario === 'split_10' && <>
                <p><strong>Técnicas:</strong> Lunes · Martes · Miércoles (lec. 1–6)</p>
                <p><strong>Generales:</strong> Miércoles (lec. 7–12) · Jueves · Viernes</p>
              </>}
              {(tipoHorario === 'split_11' || tipoHorario === 'split_12') && <>
                <p><strong>Técnicas:</strong> Lunes · Martes</p>
                <p><strong>Generales:</strong> Miércoles · Jueves · Viernes</p>
              </>}
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={guardarTipoHorario} disabled={saving}
                    className="btn-primary flex-1 disabled:opacity-60">
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
            <button onClick={() => setModalGrupos(false)}
                    className="btn-secondary flex-1">Cancelar</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}