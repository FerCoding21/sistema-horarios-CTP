import jsPDF      from 'jspdf'
import autoTable   from 'jspdf-autotable'
import * as XLSX   from 'xlsx'

const DIAS       = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']
const DIAS_LABEL = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']

const LECCIONES = [
  { num: 1,  hora: '7:00 - 7:40'   }, { num: 2,  hora: '7:40 - 8:20'   },
  { num: 3,  hora: '8:20 - 9:00'   }, { num: 4,  hora: '9:20 - 10:00'  },
  { num: 5,  hora: '10:00 - 10:40' }, { num: 6,  hora: '10:40 - 11:20' },
  { num: 7,  hora: '12:00 - 12:40' }, { num: 8,  hora: '12:40 - 1:20'  },
  { num: 9,  hora: '1:20 - 2:00'   }, { num: 10, hora: '2:20 - 3:00'   },
  { num: 11, hora: '3:00 - 3:40'   }, { num: 12, hora: '3:40 - 4:20'   },
]

const SEPARADORES = [
  { despues_de: 3, label: 'Recreo  9:00 – 9:20'    },
  { despues_de: 6, label: 'Almuerzo  11:20 – 12:00' },
  { despues_de: 9, label: 'Recreo  2:00 – 2:20'    },
]

// Devuelve la sesión que cubre la leccion num en el día dia
const sesionEn = (horario, dia, num) =>
  horario.find(l => l.dia === dia && l.leccion_inicio <= num && l.leccion_fin >= num) ?? null

// ── PDF ───────────────────────────────────────────────────────────────────────
export function exportarPDF(horario, nombreGrupo, annoLectivo, especialidad = '') {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })

  // Título
  const titulo    = `Horario – ${nombreGrupo}${especialidad ? '  ·  ' + especialidad : ''}`
  const subtitulo = `Año lectivo ${annoLectivo}`

  doc.setFontSize(14)
  doc.setTextColor(22, 101, 52)          // verde-800
  doc.setFont('helvetica', 'bold')
  doc.text(titulo, 14, 16)

  doc.setFontSize(9)
  doc.setTextColor(107, 114, 128)        // gray-500
  doc.setFont('helvetica', 'normal')
  doc.text(subtitulo, 14, 22)

  // Construir filas (una fila por lección + filas de descanso)
  const body = []

  for (const { num, hora } of LECCIONES) {
    const sep = SEPARADORES.find(s => s.despues_de === num - 1)
    if (sep) {
      body.push([{
        content:  sep.label,
        colSpan:  7,
        styles: {
          fillColor:  [243, 244, 246],
          textColor:  [107, 114, 128],
          fontStyle:  'italic',
          halign:     'center',
          fontSize:   7,
          cellPadding: 2,
        },
      }])
    }

    const row = [
      { content: String(num),
        styles: { fontStyle: 'bold', textColor: [22, 101, 52], halign: 'center' } },
      { content: hora,
        styles: { halign: 'center', textColor: [107, 114, 128], fontSize: 7 } },
    ]

    for (const dia of DIAS) {
      const s = sesionEn(horario, dia, num)
      if (s) {
        // Color diferente si es inicio vs continuación de la misma sesión
        const esInicio = s.leccion_inicio === num
        row.push({
          content: s.materia,
          styles: {
            fillColor:   esInicio ? [220, 252, 231] : [240, 253, 244],
            textColor:   [22, 101, 52],
            fontStyle:   esInicio ? 'bold' : 'normal',
            halign:      'center',
            fontSize:    7,
            cellPadding: esInicio ? 3 : 2,
          },
        })
      } else {
        row.push({ content: '', styles: { fillColor: [249, 250, 251] } })
      }
    }
    body.push(row)
  }

  autoTable(doc, {
    startY:     28,
    head: [[
      { content: 'Lecc.',    styles: { halign: 'center', cellWidth: 12 } },
      { content: 'Hora',     styles: { halign: 'center', cellWidth: 30 } },
      ...DIAS_LABEL.map(d => ({ content: d, styles: { halign: 'center' } })),
    ]],
    body,
    theme:        'grid',
    headStyles: {
      fillColor:   [22, 101, 52],
      textColor:   255,
      fontStyle:   'bold',
      fontSize:    9,
      halign:      'center',
    },
    styles: {
      fontSize:    8,
      cellPadding: 2,
      lineColor:   [229, 231, 235],
    },
    alternateRowStyles: { fillColor: false },
    columnStyles: {
      0: { cellWidth: 12 },
      1: { cellWidth: 30 },
    },
  })

  // Footer con fecha
  const fecha = new Date().toLocaleDateString('es-CR', { year: 'numeric', month: 'long', day: 'numeric' })
  const pY    = doc.internal.pageSize.height - 6
  doc.setFontSize(7)
  doc.setTextColor(156, 163, 175)
  doc.text('CTP Heredia – Sistema de Gestión de Horarios', 14, pY)
  doc.text(`Generado el ${fecha}`, doc.internal.pageSize.width - 14, pY, { align: 'right' })

  const nombreArchivo = `horario_${nombreGrupo.replace(/\s+/g, '_')}_${annoLectivo}.pdf`
  doc.save(nombreArchivo)
}


// ── Excel ─────────────────────────────────────────────────────────────────────
export function exportarExcel(horario, nombreGrupo, annoLectivo, especialidad = '') {
  const datos  = []
  const merges = []           // rangos de celdas a fusionar
  const lecToFila = {}        // { num: rowIndex (base 0) }

  // Fila de título
  datos.push([`Horario – ${nombreGrupo}${especialidad ? ' · ' + especialidad : ''}  |  Año ${annoLectivo}`])
  merges.push({ s: { r: 0, c: 0 }, e: { r: 0, c: 6 } })

  // Fila de encabezados
  datos.push(['Lecc.', 'Hora', ...DIAS_LABEL])

  let ri = 2   // índice de fila actual (después de título + header)

  for (const { num, hora } of LECCIONES) {
    const sep = SEPARADORES.find(s => s.despues_de === num - 1)
    if (sep) {
      datos.push([sep.label, '', '', '', '', '', ''])
      merges.push({ s: { r: ri, c: 0 }, e: { r: ri, c: 6 } })
      ri++
    }

    lecToFila[num] = ri

    const fila = [num, hora]
    for (const dia of DIAS) {
      const s = sesionEn(horario, dia, num)
      fila.push(s ? s.materia : '')
    }
    datos.push(fila)
    ri++
  }

  // Agregar merges verticales para sesiones que abarcan varias lecciones
  const vistos = new Set()
  for (const s of horario) {
    const key = `${s.dia}-${s.leccion_inicio}`
    if (vistos.has(key) || s.leccion_inicio === s.leccion_fin) continue
    vistos.add(key)

    const rInicio = lecToFila[s.leccion_inicio]
    const rFin    = lecToFila[s.leccion_fin]
    const col     = DIAS.indexOf(s.dia) + 2  // +2 por columnas Lecc + Hora

    if (rInicio !== undefined && rFin !== undefined && rInicio < rFin) {
      merges.push({ s: { r: rInicio, c: col }, e: { r: rFin, c: col } })
    }
  }

  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.aoa_to_sheet(datos)
  ws['!merges'] = merges

  // Anchos de columna
  ws['!cols'] = [
    { wch: 7  },   // Lecc.
    { wch: 16 },   // Hora
    { wch: 26 },   // Lunes
    { wch: 26 },   // Martes
    { wch: 26 },   // Miércoles
    { wch: 26 },   // Jueves
    { wch: 26 },   // Viernes
  ]

  const nombreHoja = nombreGrupo.slice(0, 31).replace(/[\\/*?[\]:]/g, '')
  XLSX.utils.book_append_sheet(wb, ws, nombreHoja)

  const nombreArchivo = `horario_${nombreGrupo.replace(/\s+/g, '_')}_${annoLectivo}.xlsx`
  XLSX.writeFile(wb, nombreArchivo)
}
