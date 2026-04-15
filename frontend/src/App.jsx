import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout        from './components/Layout'
import Login         from './pages/Login'
import Dashboard     from './pages/Dashboard'
import Materias      from './pages/Materias'
import Grupos        from './pages/Grupos'
import Especialidades from './pages/Especialidades'
import Horarios      from './pages/Horarios'

function RutaProtegida({ children }) {
  const { usuario, cargando } = useAuth()
  if (cargando) return (
    <div className="min-h-screen flex items-center justify-center bg-verde-600">
      <div className="text-white text-center">
        <div className="w-8 h-8 border-2 border-white/30 border-t-white
                        rounded-full animate-spin mx-auto mb-3" />
        <p className="text-sm text-verde-200">Cargando...</p>
      </div>
    </div>
  )
  return usuario ? children : <Navigate to="/login" replace />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={
        <RutaProtegida>
          <Layout />
        </RutaProtegida>
      }>
        <Route index                element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard"     element={<Dashboard />} />
        <Route path="materias"      element={<Materias />} />
        <Route path="grupos"        element={<Grupos />} />
        <Route path="especialidades" element={<Especialidades />} />
        <Route path="horarios"      element={<Horarios />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
