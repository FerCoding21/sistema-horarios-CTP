import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, BookOpen, GraduationCap,
  Calendar, LogOut, Menu, X, ChevronRight, Award
} from 'lucide-react'

const navItems = [
  { to: '/dashboard',      icon: LayoutDashboard, label: 'Dashboard'      },
  { to: '/materias',       icon: BookOpen,         label: 'Materias'       },
  { to: '/grupos',         icon: GraduationCap,    label: 'Grupos'         },
  { to: '/especialidades', icon: Award,            label: 'Especialidades' },
  { to: '/horarios',       icon: Calendar,         label: 'Horarios'       },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { usuario, logout }           = useAuth()
  const navigate                      = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">

      {/* ── SIDEBAR ── */}
      <aside className={`
        flex flex-col transition-all duration-300 ease-in-out
        bg-verde-700 text-white flex-shrink-0
        ${sidebarOpen ? 'w-64' : 'w-16'}
      `}>

        {/* Logo / Header */}
        <div className="flex items-center justify-between px-4 py-5 border-b border-verde-600">
          {sidebarOpen && (
            <div className="fade-in">
              <p className="font-display text-lg font-bold text-white leading-tight">
                CTP Heredia
              </p>
              <p className="text-verde-300 text-xs">Horarios Académicos</p>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 rounded-lg hover:bg-verde-600 transition-colors ml-auto">
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>

        {/* Navegación */}
        <nav className="flex-1 py-4 space-y-1 px-2 overflow-y-auto">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `
                flex items-center gap-3 px-3 py-2.5 rounded-lg
                transition-all duration-150 group relative
                ${isActive
                  ? 'bg-verde-500 text-white shadow-sm'
                  : 'text-verde-200 hover:bg-verde-600 hover:text-white'
                }
              `}>
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2
                                     w-1 h-6 bg-amarillo-400 rounded-r-full" />
                  )}
                  <Icon size={18} className="flex-shrink-0" />
                  {sidebarOpen && (
                    <span className="text-sm font-medium slide-in">{label}</span>
                  )}
                  {sidebarOpen && isActive && (
                    <ChevronRight size={14} className="ml-auto opacity-60" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Usuario y logout */}
        <div className="border-t border-verde-600 p-3">
          {sidebarOpen && (
            <div className="mb-2 px-2 fade-in">
              <p className="text-white text-sm font-medium truncate">
                {usuario?.nombre}
              </p>
              <p className="text-verde-300 text-xs capitalize">
                {usuario?.rol}
              </p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-3 py-2 rounded-lg
                       text-verde-300 hover:bg-verde-600 hover:text-white
                       transition-colors duration-150">
            <LogOut size={18} className="flex-shrink-0" />
            {sidebarOpen && <span className="text-sm">Cerrar sesión</span>}
          </button>
        </div>
      </aside>

      {/* ── CONTENIDO PRINCIPAL ── */}
      <main className="flex-1 overflow-y-auto">
        <header className="bg-white border-b border-gray-200 px-8 py-4
                           flex items-center justify-between sticky top-0 z-10">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider font-medium">
              Año Lectivo 2026
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="badge-verde">{usuario?.rol}</span>
            <span className="text-sm text-gray-600">{usuario?.email}</span>
          </div>
        </header>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
