import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/axios'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    const usuarioGuardado = localStorage.getItem('usuario')
    const token           = localStorage.getItem('token')
    if (usuarioGuardado && token) {
      setUsuario(JSON.parse(usuarioGuardado))
    }
    setCargando(false)
  }, [])

  const login = async (email, password) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const res = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    localStorage.setItem('token',   res.data.access_token)
    localStorage.setItem('usuario', JSON.stringify(res.data))
    setUsuario(res.data)
    return res.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('usuario')
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ usuario, login, logout, cargando }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)