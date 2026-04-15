import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'

// Pasos del flujo de reset
const PASO = { LOGIN: 'login', SOLICITAR: 'solicitar', CONFIRMAR: 'confirmar' }

export default function Login() {
  const [paso,        setPaso]        = useState(PASO.LOGIN)

  // Login
  const [email,       setEmail]       = useState('')
  const [password,    setPassword]    = useState('')

  // Reset
  const [resetEmail,  setResetEmail]  = useState('')
  const [otp,         setOtp]         = useState('')
  const [pwNuevo,     setPwNuevo]     = useState('')
  const [pwConfirm,   setPwConfirm]   = useState('')

  const [error,       setError]       = useState('')
  const [mensaje,     setMensaje]     = useState('')
  const [cargando,    setCargando]    = useState(false)

  const { login }  = useAuth()
  const navigate   = useNavigate()

  // ── Login ──────────────────────────────────────────────────────
  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setCargando(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión')
    } finally {
      setCargando(false)
    }
  }

  // ── Paso 1 reset: solicitar OTP ────────────────────────────────
  const handleSolicitarOtp = async (e) => {
    e.preventDefault()
    setError('')
    setCargando(true)
    try {
      const res = await api.post('/auth/solicitar-reset', { email: resetEmail })
      setMensaje(res.data.mensaje)
      setPaso(PASO.CONFIRMAR)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al enviar el código')
    } finally {
      setCargando(false)
    }
  }

  // ── Paso 2 reset: confirmar OTP y nueva contraseña ─────────────
  const handleConfirmarReset = async (e) => {
    e.preventDefault()
    setError('')
    if (pwNuevo !== pwConfirm) {
      setError('Las contraseñas no coinciden')
      return
    }
    if (pwNuevo.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres')
      return
    }
    setCargando(true)
    try {
      const res = await api.post('/auth/confirmar-reset', {
        email:          resetEmail,
        otp:            otp.trim(),
        password_nuevo: pwNuevo,
      })
      setMensaje(res.data.mensaje)
      // Volver al login después de 2s
      setTimeout(() => {
        setPaso(PASO.LOGIN)
        setMensaje('')
        setOtp('')
        setPwNuevo('')
        setPwConfirm('')
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Código incorrecto o expirado')
    } finally {
      setCargando(false)
    }
  }

  const volverAlLogin = () => {
    setPaso(PASO.LOGIN)
    setError('')
    setMensaje('')
  }

  // ── Render ─────────────────────────────────────────────────────
  return (
    <div className="min-h-screen flex items-center justify-center p-4"
         style={{ background: 'linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%)' }}>

      {/* Patrón de fondo */}
      <div className="absolute inset-0 opacity-5"
           style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '32px 32px' }} />

      <div className="relative w-full max-w-md fade-in">

        {/* Header institucional */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full
                          bg-white/10 backdrop-blur border border-white/20 mb-4">
            <span className="text-4xl">🏫</span>
          </div>
          <h1 className="text-white font-display text-3xl font-bold leading-tight">
            CTP Heredia
          </h1>
          <p className="text-verde-200 text-sm mt-1 font-sans">
            Sistema de Gestión de Horarios
          </p>
          <div className="w-16 h-0.5 bg-amarillo-400 mx-auto mt-3 rounded-full" />
        </div>

        {/* ── Card ── */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">

          {/* ════ LOGIN ════ */}
          {paso === PASO.LOGIN && (
            <>
              <h2 className="text-verde-700 font-display text-xl font-bold mb-6 text-center">
                Iniciar Sesión
              </h2>

              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="label">Correo electrónico</label>
                  <input type="email" className="input"
                         placeholder="usuario@ctp.ed.cr"
                         value={email} onChange={e => setEmail(e.target.value)} required />
                </div>

                <div>
                  <label className="label">Contraseña</label>
                  <input type="password" className="input"
                         placeholder="••••••••"
                         value={password} onChange={e => setPassword(e.target.value)} required />
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-600
                                  text-sm rounded-lg px-4 py-3 fade-in">
                    {error}
                  </div>
                )}

                <button type="submit" disabled={cargando}
                        className="btn-primary w-full py-3 text-base mt-2
                                   disabled:opacity-60 disabled:cursor-not-allowed">
                  {cargando ? 'Ingresando...' : 'Ingresar al sistema'}
                </button>
              </form>

              <div className="mt-5 text-center">
                <button onClick={() => { setPaso(PASO.SOLICITAR); setError('') }}
                        className="text-sm text-verde-600 hover:text-verde-800
                                   hover:underline transition-colors">
                  ¿Olvidaste tu contraseña?
                </button>
              </div>
            </>
          )}

          {/* ════ PASO 1: SOLICITAR OTP ════ */}
          {paso === PASO.SOLICITAR && (
            <>
              <button onClick={volverAlLogin}
                      className="flex items-center gap-1.5 text-sm text-gray-400
                                 hover:text-gray-600 mb-5 transition-colors">
                ← Volver al inicio de sesión
              </button>

              <h2 className="text-verde-700 font-display text-xl font-bold mb-2 text-center">
                Restablecer contraseña
              </h2>
              <p className="text-gray-400 text-sm text-center mb-6">
                Ingresá tu correo de administrador y te enviaremos un código de verificación.
              </p>

              <form onSubmit={handleSolicitarOtp} className="space-y-4">
                <div>
                  <label className="label">Ingresa tu Correo</label>
                  <input type="email" className="input"
                         placeholder="admin@ctp.ed.cr"
                         value={resetEmail}
                         onChange={e => setResetEmail(e.target.value)} required />
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-600
                                  text-sm rounded-lg px-4 py-3 fade-in">
                    {error}
                  </div>
                )}

                <button type="submit" disabled={cargando}
                        className="btn-primary w-full py-3 text-base
                                   disabled:opacity-60 disabled:cursor-not-allowed">
                  {cargando ? 'Enviando...' : 'Enviar código'}
                </button>
              </form>
            </>
          )}

          {/* ════ PASO 2: CONFIRMAR OTP + NUEVA CONTRASEÑA ════ */}
          {paso === PASO.CONFIRMAR && (
            <>
              <button onClick={() => { setPaso(PASO.SOLICITAR); setError('') }}
                      className="flex items-center gap-1.5 text-sm text-gray-400
                                 hover:text-gray-600 mb-5 transition-colors">
                ← Cambiar correo
              </button>

              <h2 className="text-verde-700 font-display text-xl font-bold mb-2 text-center">
                Ingresá el código
              </h2>

              {mensaje && (
                <div className="bg-verde-50 border border-verde-200 text-verde-700
                                text-sm rounded-lg px-4 py-3 mb-4 fade-in text-center">
                  {mensaje}
                </div>
              )}

              <p className="text-gray-400 text-sm text-center mb-6">
                Revisá tu correo <strong className="text-gray-600">{resetEmail}</strong>.
                El código expira en <strong className="text-gray-600">15 minutos</strong>.
              </p>

              <form onSubmit={handleConfirmarReset} className="space-y-4">
                <div>
                  <label className="label">Código de 6 dígitos</label>
                  <input
                    type="text"
                    className="input text-center text-2xl font-mono tracking-[0.5em] font-bold"
                    placeholder="000000"
                    maxLength={6}
                    value={otp}
                    onChange={e => setOtp(e.target.value.replace(/\D/g, ''))}
                    required
                  />
                </div>

                <div>
                  <label className="label">Nueva contraseña</label>
                  <input type="password" className="input"
                         placeholder="Mínimo 8 caracteres"
                         value={pwNuevo}
                         onChange={e => setPwNuevo(e.target.value)} required />
                </div>

                <div>
                  <label className="label">Confirmar contraseña</label>
                  <input type="password" className="input"
                         placeholder="Repetí la contraseña"
                         value={pwConfirm}
                         onChange={e => setPwConfirm(e.target.value)} required />
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-600
                                  text-sm rounded-lg px-4 py-3 fade-in">
                    {error}
                  </div>
                )}

                <button type="submit" disabled={cargando || otp.length !== 6}
                        className="btn-primary w-full py-3 text-base
                                   disabled:opacity-60 disabled:cursor-not-allowed">
                  {cargando ? 'Verificando...' : 'Restablecer contraseña'}
                </button>

                <button type="button"
                        onClick={handleSolicitarOtp}
                        disabled={cargando}
                        className="w-full text-sm text-verde-600 hover:text-verde-800
                                   hover:underline transition-colors py-1">
                  ¿No recibiste el código? Reenviar
                </button>
              </form>
            </>
          )}
        </div>

        <p className="text-center text-verde-300 text-xs mt-6">
          Colegio Técnico Profesional de Heredia © 2025
        </p>
      </div>
    </div>
  )
}
