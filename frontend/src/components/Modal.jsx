import { X } from 'lucide-react'
import { useEffect } from 'react'

export default function Modal({ open, onClose, title, children, size = 'md' }) {
  // Cerrar con Escape
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') onClose() }
    if (open) window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, onClose])

  if (!open) return null

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"
           onClick={onClose} />

      {/* Modal */}
      <div className={`relative bg-white rounded-2xl shadow-2xl w-full
                       ${sizes[size]} max-h-[90vh] overflow-y-auto fade-in`}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4
                        border-b border-gray-100 sticky top-0 bg-white rounded-t-2xl">
          <h3 className="font-display text-lg font-bold text-verde-700">
            {title}
          </h3>
          <button onClick={onClose}
                  className="p-1.5 rounded-lg hover:bg-gray-100
                             text-gray-400 hover:text-gray-600 transition-colors">
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-5">
          {children}
        </div>
      </div>
    </div>
  )
}