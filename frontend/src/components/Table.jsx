export default function Table({ columns, data, loading, emptyMessage = "No hay registros" }) {
  if (loading) return (
    <div className="flex items-center justify-center py-16">
      <div className="w-8 h-8 border-2 border-verde-200 border-t-verde-500
                      rounded-full animate-spin" />
    </div>
  )

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-100">
      <table className="w-full text-sm">
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col.key}
                  className="table-header px-4 py-3 text-left font-medium first:rounded-tl-xl last:rounded-tr-xl">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length}
                  className="text-center py-12 text-gray-400">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={row.id ?? i} className="table-row">
                {columns.map(col => (
                  <td key={col.key} className="px-4 py-3 text-gray-700">
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}