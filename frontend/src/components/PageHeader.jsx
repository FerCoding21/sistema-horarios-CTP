export default function PageHeader({ title, subtitle, action }) {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-verde-700">{title}</h1>
        {subtitle && (
          <p className="text-gray-500 text-sm mt-1">{subtitle}</p>
        )}
        <div className="w-10 h-0.5 bg-amarillo-400 mt-2 rounded-full" />
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  )
}