import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { BookOpen, GraduationCap, Award, Calendar } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '../api/axios'

export default function Dashboard() {
  const { usuario } = useAuth()
  const [stats, setStats] = useState({ materias: 0, grupos: 0, especialidades: 0 })

  useEffect(() => {
    const cargar = async () => {
      try {
        const [mats, grps, esps] = await Promise.all([
          api.get('/materias/'),
          api.get('/grupos/'),
          api.get('/especialidades/')
        ])
        setStats({
          materias:      mats.data.length,
          grupos:        grps.data.length,
          especialidades: esps.data.length
        })
      } catch {}
    }
    cargar()
  }, [])

  const cards = [
    { label: 'Materias',       value: stats.materias,       icon: BookOpen,      color: 'bg-verde-500', to: '/materias'       },
    { label: 'Grupos',         value: stats.grupos,         icon: GraduationCap, color: 'bg-verde-600', to: '/grupos'         },
    { label: 'Especialidades', value: stats.especialidades, icon: Award,         color: 'bg-verde-700', to: '/especialidades' },
  ]

  return (
    <div className="fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-verde-700">
          Bienvenido, {usuario?.nombre}
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Sistema de Horarios — CTP Heredia
        </p>
        <div className="w-12 h-0.5 bg-amarillo-400 mt-3 rounded-full" />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-8">
        {cards.map(({ label, value, icon: Icon, color, to }, i) => (
          <Link key={label} to={to}
            className="card flex items-center gap-4 fade-in hover:shadow-md transition-shadow"
            style={{ animationDelay: `${i * 80}ms` }}>
            <div className={`${color} p-3 rounded-xl text-white flex-shrink-0`}>
              <Icon size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-800">{value}</p>
              <p className="text-sm text-gray-500">{label}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Acceso rápido */}
      <div className="card">
        <h2 className="text-base font-semibold text-gray-700 mb-4 flex items-center gap-2">
          <Calendar size={18} className="text-verde-500" />
          Acceso rápido
        </h2>
        <div className="grid grid-cols-2 gap-3">
          <Link to="/grupos"
            className="flex items-center gap-3 p-4 rounded-xl border border-gray-100
                       hover:border-verde-200 hover:bg-verde-50 transition-all group">
            <GraduationCap size={20} className="text-verde-500 group-hover:scale-110 transition-transform" />
            <div>
              <p className="text-sm font-medium text-gray-700">Asignar materias a grupos</p>
              <p className="text-xs text-gray-400">Configura el plan de cada grupo</p>
            </div>
          </Link>
          <Link to="/horarios"
            className="flex items-center gap-3 p-4 rounded-xl border border-gray-100
                       hover:border-verde-200 hover:bg-verde-50 transition-all group">
            <Calendar size={20} className="text-verde-500 group-hover:scale-110 transition-transform" />
            <div>
              <p className="text-sm font-medium text-gray-700">Generar horarios</p>
              <p className="text-xs text-gray-400">Ejecutar el algoritmo automático</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}
