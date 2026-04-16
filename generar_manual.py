"""
Genera el manual de usuario del Sistema de Gestión de Horarios CTP Heredia.
Ejecutar: python generar_manual.py
Requiere: pip install reportlab
"""

from reportlab.lib.pagesizes   import A4
from reportlab.lib.styles      import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units       import cm
from reportlab.lib.colors      import HexColor, white, black
from reportlab.platypus        import (SimpleDocTemplate, Paragraph, Spacer,
                                       Table, TableStyle, PageBreak,
                                       HRFlowable, KeepTogether)
from reportlab.lib.enums       import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus        import ListFlowable, ListItem
from reportlab.lib             import colors
import datetime

# ── Colores institucionales ────────────────────────────────────────
VERDE_OSCURO  = HexColor('#166534')
VERDE_MEDIO   = HexColor('#15803d')
VERDE_CLARO   = HexColor('#dcfce7')
VERDE_BORDE   = HexColor('#86efac')
AMARILLO      = HexColor('#ca8a04')
AMARILLO_BG   = HexColor('#fefce8')
AMARILLO_BRD  = HexColor('#fde047')
ROJO_BG       = HexColor('#fef2f2')
ROJO_BRD      = HexColor('#fca5a5')
ROJO_TEXT     = HexColor('#991b1b')
GRIS_CLARO    = HexColor('#f9fafb')
GRIS_BORDE    = HexColor('#e5e7eb')
GRIS_TEXT     = HexColor('#6b7280')
AZUL_BG       = HexColor('#eff6ff')
AZUL_BRD      = HexColor('#93c5fd')
AZUL_TEXT     = HexColor('#1e40af')

# ── Estilos ────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def estilo(name, **kwargs):
    base = kwargs.pop('parent', 'Normal')
    s = ParagraphStyle(name, parent=styles[base], **kwargs)
    return s

S_TITULO       = estilo('Titulo',      fontSize=26, textColor=VERDE_OSCURO,
                         fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6)
S_SUBTITULO    = estilo('Subtitulo',   fontSize=13, textColor=GRIS_TEXT,
                         fontName='Helvetica',      alignment=TA_CENTER, spaceAfter=4)
S_SECCION      = estilo('Seccion',     fontSize=15, textColor=VERDE_OSCURO,
                         fontName='Helvetica-Bold', spaceBefore=18, spaceAfter=8)
S_SUBSECCION   = estilo('Subseccion',  fontSize=12, textColor=VERDE_MEDIO,
                         fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=5)
S_CUERPO       = estilo('Cuerpo',      fontSize=10, textColor=HexColor('#374151'),
                         fontName='Helvetica',      leading=15,  spaceAfter=5,
                         alignment=TA_JUSTIFY)
S_LISTA        = estilo('Lista',       fontSize=10, textColor=HexColor('#374151'),
                         fontName='Helvetica',      leading=14,  spaceAfter=3,
                         leftIndent=12)
S_NOTA_TITULO  = estilo('NotaTitulo',  fontSize=10, textColor=AMARILLO,
                         fontName='Helvetica-Bold', spaceAfter=2)
S_NOTA_CUERPO  = estilo('NotaCuerpo',  fontSize=9,  textColor=HexColor('#713f12'),
                         fontName='Helvetica',      leading=13)
S_ALERTA_TIT   = estilo('AlertaTit',   fontSize=10, textColor=ROJO_TEXT,
                         fontName='Helvetica-Bold', spaceAfter=2)
S_ALERTA_CUERPO= estilo('AlertaCuerpo',fontSize=9,  textColor=ROJO_TEXT,
                         fontName='Helvetica',      leading=13)
S_INFO_CUERPO  = estilo('InfoCuerpo',  fontSize=9,  textColor=AZUL_TEXT,
                         fontName='Helvetica',      leading=13)
S_PASO_NUM     = estilo('PasoNum',     fontSize=28, textColor=white,
                         fontName='Helvetica-Bold', alignment=TA_CENTER)
S_CAMPO        = estilo('Campo',       fontSize=9,  textColor=HexColor('#374151'),
                         fontName='Helvetica-Bold')
S_CAMPO_DESC   = estilo('CampoDesc',   fontSize=9,  textColor=GRIS_TEXT,
                         fontName='Helvetica',      leading=12)
S_PIE          = estilo('Pie',         fontSize=8,  textColor=GRIS_TEXT,
                         fontName='Helvetica',      alignment=TA_CENTER)
S_TABLA_HDR    = estilo('TablaHdr',    fontSize=9,  textColor=white,
                         fontName='Helvetica-Bold', alignment=TA_CENTER)
S_TABLA_CELDA  = estilo('TablaCelda',  fontSize=9,  textColor=HexColor('#374151'),
                         fontName='Helvetica',      alignment=TA_CENTER)


# ── Helpers ────────────────────────────────────────────────────────

def caja_nota(titulo, texto):
    """Recuadro amarillo de advertencia/recomendación."""
    contenido = [
        [Paragraph(f'⚠  {titulo}', S_NOTA_TITULO)],
        [Paragraph(texto, S_NOTA_CUERPO)],
    ]
    t = Table(contenido, colWidths=[15.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), AMARILLO_BG),
        ('BOX',         (0,0), (-1,-1), 1, AMARILLO_BRD),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING',(0,0), (-1,-1), 10),
        ('TOPPADDING',  (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[AMARILLO_BG]),
    ]))
    return t

def caja_alerta(titulo, texto):
    """Recuadro rojo de error crítico."""
    contenido = [
        [Paragraph(f'✖  {titulo}', S_ALERTA_TIT)],
        [Paragraph(texto, S_ALERTA_CUERPO)],
    ]
    t = Table(contenido, colWidths=[15.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), ROJO_BG),
        ('BOX',         (0,0), (-1,-1), 1, ROJO_BRD),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING',(0,0), (-1,-1), 10),
        ('TOPPADDING',  (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
    ]))
    return t

def caja_info(texto):
    """Recuadro azul informativo."""
    contenido = [[Paragraph(f'ℹ  {texto}', S_INFO_CUERPO)]]
    t = Table(contenido, colWidths=[15.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), AZUL_BG),
        ('BOX',         (0,0), (-1,-1), 1, AZUL_BRD),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING',(0,0), (-1,-1), 10),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
    ]))
    return t

def encabezado_paso(numero, titulo):
    """Encabezado visual de cada paso numerado."""
    num_cell  = Paragraph(str(numero), S_PASO_NUM)
    tit_cell  = Paragraph(titulo, estilo(f'PasoTit{numero}',
                           fontSize=14, textColor=white,
                           fontName='Helvetica-Bold',
                           leading=17))
    t = Table([[num_cell, tit_cell]], colWidths=[1.8*cm, 13.7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), VERDE_OSCURO),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING',  (0,0), (0,0),   8),
        ('LEFTPADDING',  (1,0), (1,0),   14),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING',   (0,0), (-1,-1), 10),
        ('BOTTOMPADDING',(0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', (0,0), (-1,-1), [6,6,6,6]),
    ]))
    return t

def tabla_campos(filas):
    """Tabla de dos columnas: Campo | Descripción."""
    data = [[Paragraph('Campo', S_TABLA_HDR),
             Paragraph('Descripción', S_TABLA_HDR)]]
    for campo, desc in filas:
        data.append([Paragraph(campo, S_CAMPO),
                     Paragraph(desc, S_CAMPO_DESC)])
    t = Table(data, colWidths=[4.5*cm, 11*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0),  VERDE_OSCURO),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [white, GRIS_CLARO]),
        ('BOX',          (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('INNERGRID',    (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))
    return t

def li(texto):
    return ListItem(Paragraph(texto, S_LISTA), bulletColor=VERDE_MEDIO,
                    leftIndent=16, bulletIndent=4)

def lista(*items):
    return ListFlowable([li(i) for i in items],
                        bulletType='bullet', bulletFontSize=8,
                        leftIndent=0, spaceBefore=2, spaceAfter=4)


# ── Páginas especiales ─────────────────────────────────────────────

def portada():
    fecha = datetime.date.today().strftime('%B %Y').capitalize()
    elems = []
    elems.append(Spacer(1, 3.5*cm))

    # Bloque verde superior
    bloque = Table(
        [[Paragraph('📅', estilo('Icon', fontSize=40, alignment=TA_CENTER,
                                  textColor=white, spaceAfter=0))],
         [Paragraph('CTP Heredia', estilo('PortTit', fontSize=22,
                                           textColor=white, fontName='Helvetica-Bold',
                                           alignment=TA_CENTER, spaceAfter=4))],
         [Paragraph('Sistema de Gestión de Horarios', estilo('PortSub', fontSize=12,
                                           textColor=HexColor('#bbf7d0'),
                                           fontName='Helvetica', alignment=TA_CENTER))]],
        colWidths=[15.5*cm])
    bloque.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), VERDE_OSCURO),
        ('TOPPADDING',   (0,0), (-1,-1), 22),
        ('BOTTOMPADDING',(0,0), (-1,-1), 22),
        ('LEFTPADDING',  (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    elems.append(bloque)
    elems.append(Spacer(1, 0.8*cm))

    elems.append(Paragraph('Manual de Usuario', S_TITULO))
    elems.append(HRFlowable(width='60%', thickness=2,
                             color=AMARILLO, spaceAfter=10,
                             hAlign='CENTER'))
    elems.append(Paragraph('Guía paso a paso para la configuración y uso del sistema',
                            S_SUBTITULO))
    elems.append(Spacer(1, 2*cm))

    # Índice de pasos
    pasos = [
        ('1', 'Ingreso de Especialidades'),
        ('2', 'Ingreso de Grupos'),
        ('3', 'Asignación de Especialidades a Grupos'),
        ('4', 'Ingreso de Materias'),
        ('5', 'Generación y Visualización del Horario'),
    ]
    idx_data = [[Paragraph(n, estilo(f'IdxN{n}', fontSize=13, textColor=VERDE_OSCURO,
                                      fontName='Helvetica-Bold', alignment=TA_CENTER)),
                 Paragraph(t, estilo(f'IdxT{n}', fontSize=11, textColor=HexColor('#374151'),
                                      fontName='Helvetica'))]
                for n, t in pasos]
    idx = Table(idx_data, colWidths=[1.5*cm, 12*cm])
    idx.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [VERDE_CLARO, white]),
        ('BOX',            (0,0), (-1,-1), 0.5, VERDE_BORDE),
        ('INNERGRID',      (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('LEFTPADDING',    (0,0), (-1,-1), 10),
        ('TOPPADDING',     (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 8),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elems.append(idx)
    elems.append(Spacer(1, 2*cm))
    elems.append(Paragraph(f'Versión 1.0  ·  {fecha}  ·  Colegio Técnico Profesional de Heredia',
                            S_PIE))
    return elems


# ── Contenido ──────────────────────────────────────────────────────

def seccion_especialidades():
    e = []
    e.append(PageBreak())
    e.append(encabezado_paso(1, 'Ingreso de Especialidades'))
    e.append(Spacer(1, 0.4*cm))
    e.append(Paragraph(
        'Las <b>especialidades</b> representan las carreras técnicas que ofrece el colegio. '
        'Cada grupo pertenece a una o dos especialidades según su conformación. '
        'Este es el primer dato que se debe ingresar, ya que los grupos y las materias técnicas '
        'dependen de ellas.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('¿Dónde ingresar?', S_SUBSECCION))
    e.append(Paragraph(
        'En el menú lateral seleccioná <b>Especialidades</b>. Usá el botón '
        '<b>"Nueva Especialidad"</b> para agregar cada una.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('Campos del formulario', S_SUBSECCION))
    e.append(tabla_campos([
        ('Nombre',  'Nombre completo de la especialidad. Ejemplo: <i>Mecánica de Precisión</i>, '
                    '<i>Dibujo Técnico</i>, <i>Electrotecnia</i>.'),
        ('Código',  'Identificador corto único. Ejemplos: <i>MP</i>, <i>DT</i>, <i>ET</i>. '
                    'Se usa para identificar la especialidad rápidamente en el sistema.'),
    ]))
    e.append(Spacer(1, 0.4*cm))

    e.append(caja_info(
        'Ingresá todas las especialidades antes de continuar con los grupos. '
        'Una vez que un grupo hace referencia a una especialidad, no se puede eliminar.'))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('Ejemplo de especialidades del CTP Heredia:', S_SUBSECCION))
    data = [
        [Paragraph('Nombre', S_TABLA_HDR), Paragraph('Código', S_TABLA_HDR)],
        [Paragraph('Mecánica de Precisión',    S_TABLA_CELDA), Paragraph('MP', S_TABLA_CELDA)],
        [Paragraph('Dibujo Técnico',            S_TABLA_CELDA), Paragraph('DT', S_TABLA_CELDA)],
        [Paragraph('Electrotecnia',             S_TABLA_CELDA), Paragraph('ET', S_TABLA_CELDA)],
        [Paragraph('Informática y Redes',       S_TABLA_CELDA), Paragraph('IR', S_TABLA_CELDA)],
        [Paragraph('Secretariado Ejecutivo',    S_TABLA_CELDA), Paragraph('SE', S_TABLA_CELDA)],
        [Paragraph('Contabilidad y Finanzas',   S_TABLA_CELDA), Paragraph('CF', S_TABLA_CELDA)],
    ]
    t = Table(data, colWidths=[10*cm, 5.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  VERDE_OSCURO),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [white, GRIS_CLARO]),
        ('BOX',           (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    e.append(t)
    return e


def seccion_grupos():
    e = []
    e.append(PageBreak())
    e.append(encabezado_paso(2, 'Ingreso de Grupos'))
    e.append(Spacer(1, 0.4*cm))
    e.append(Paragraph(
        'Los <b>grupos</b> son las secciones de estudiantes que recibirán un horario. '
        'En el CTP Heredia los grupos se identifican por nivel y número de sección: '
        '10-1, 10-2, … 12-10.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('¿Dónde ingresar?', S_SUBSECCION))
    e.append(Paragraph(
        'En el menú lateral seleccioná <b>Grupos</b>. Usá el botón <b>"Nuevo Grupo"</b>.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('Campos del formulario', S_SUBSECCION))
    e.append(tabla_campos([
        ('Nombre',  'Nombre del grupo con el formato <i>nivel-sección</i>. '
                    'Ejemplos: <b>10-1</b>, <b>11-5</b>, <b>12-10</b>.'),
        ('Nivel',   'Año académico del grupo. Debe ser <b>10</b>, <b>11</b> o <b>12</b>. '
                    'Este dato es fundamental porque el sistema filtra las materias '
                    'disponibles según el nivel del grupo.'),
    ]))
    e.append(Spacer(1, 0.4*cm))

    e.append(caja_nota(
        'Ingresá el nivel correctamente',
        'El nivel (10, 11 o 12) determina qué materias puede recibir el grupo. '
        'Si el nivel está mal ingresado, el sistema no encontrará las materias '
        'correspondientes y el horario no se podrá generar correctamente.'))
    e.append(Spacer(1, 0.4*cm))

    e.append(Paragraph(
        'Una vez ingresado el grupo, la especialidad se asigna en el paso siguiente. '
        'No es necesario asignarla en este formulario.', S_CUERPO))
    return e


def seccion_asignacion():
    e = []
    e.append(PageBreak())
    e.append(encabezado_paso(3, 'Asignación de Especialidades a Grupos'))
    e.append(Spacer(1, 0.4*cm))
    e.append(Paragraph(
        'Cada grupo debe tener asignada al menos una especialidad. Esta relación le indica '
        'al sistema cuáles materias técnicas corresponden al grupo y cómo organizar '
        'las pistas de horario.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('¿Dónde asignar?', S_SUBSECCION))
    e.append(Paragraph(
        'En la sección <b>Grupos</b>, buscá el grupo deseado y usá el botón '
        '<b>"Asignar Especialidad"</b> o el ícono de edición para añadirla.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('Grupos con una especialidad (caso normal)', S_SUBSECCION))
    e.append(Paragraph(
        'La mayoría de los grupos tiene una sola especialidad. Por ejemplo, el grupo '
        '<b>10-1</b> pertenece únicamente a <i>Mecánica de Precisión</i>. '
        'En este caso el horario técnico se genera de forma directa.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('Grupos con dos especialidades (pistas paralelas)', S_SUBSECCION))
    e.append(Paragraph(
        'Algunos grupos están conformados por estudiantes de dos especialidades distintas '
        'que comparten las materias académicas pero reciben lecciones técnicas '
        'de manera simultánea en aulas separadas. Por ejemplo, un grupo puede tener '
        '15 estudiantes de <i>Mecánica de Precisión</i> y 15 de <i>Dibujo Técnico</i>.', S_CUERPO))
    e.append(Spacer(1, 0.2*cm))

    e.append(caja_nota(
        'Grupos de doble especialidad',
        'Cuando un grupo tiene dos especialidades asignadas, el sistema genera dos '
        'pistas de horario paralelas para las materias técnicas, garantizando que '
        'no se solapen entre sí. Las materias académicas (Matemáticas, Español, etc.) '
        'son compartidas por ambas pistas y aparecen en ambos horarios.'))
    e.append(Spacer(1, 0.4*cm))

    e.append(caja_info(
        'Verificá que todos los grupos tengan al menos una especialidad asignada antes '
        'de intentar generar el horario. Grupos sin especialidad causarán errores en la generación.'))
    return e


def seccion_materias():
    e = []
    e.append(PageBreak())
    e.append(encabezado_paso(4, 'Ingreso de Materias'))
    e.append(Spacer(1, 0.4*cm))
    e.append(Paragraph(
        'El ingreso correcto de las materias es el paso más importante y delicado '
        'de la configuración. Un error aquí afecta directamente la calidad del horario generado. '
        'Leé esta sección con atención antes de comenzar.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('¿Dónde ingresar?', S_SUBSECCION))
    e.append(Paragraph(
        'En el menú lateral seleccioná <b>Materias</b>. Usá el botón <b>"Nueva Materia"</b>.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('Campos del formulario', S_SUBSECCION))
    e.append(tabla_campos([
        ('Nombre',
         'Nombre descriptivo de la materia. Si la misma materia tiene diferente carga horaria '
         'según el nivel, se recomienda incluir el nivel en el nombre. '
         'Ejemplo: <i>Matemáticas 10°</i>, <i>Matemáticas 11°</i>.'),
        ('Código',
         'Identificador único corto. Ejemplo: <i>MAT10</i>, <i>MAT11</i>, <i>ESP</i>, <i>MMHH</i>.'),
        ('Lecciones Semanales',
         'Cantidad total de lecciones (períodos de 40 min) que la materia recibe por semana. '
         'Ejemplo: Matemáticas = 5, Inglés = 4, Mecanizado = 12.'),
        ('Bloques por Sesión',
         'Cantidad de bloques de 3 lecciones consecutivas que se imparten en una sola sesión. '
         'Ver explicación detallada más adelante.'),
        ('Especialidad',
         'Solo para materias técnicas. Seleccioná la especialidad a la que pertenece. '
         'Para materias académicas dejá este campo vacío (sin selección).'),
        ('Niveles',
         'Marcá los niveles (10°, 11°, 12°) a los que aplica esta materia. '
         'El sistema asignará la materia únicamente a grupos del nivel correspondiente.'),
    ]))
    e.append(Spacer(1, 0.5*cm))

    # ── Lecciones semanales ──
    e.append(Paragraph('¿Qué son las Lecciones Semanales?', S_SUBSECCION))
    e.append(Paragraph(
        'Una <b>lección</b> equivale a un período de 40 minutos de clase. '
        'Las lecciones semanales indican cuántos períodos de 40 minutos recibirá '
        'esa materia a lo largo de una semana completa.', S_CUERPO))
    e.append(Spacer(1, 0.2*cm))

    lec_data = [
        [Paragraph('Materia', S_TABLA_HDR),
         Paragraph('Lecciones Semanales', S_TABLA_HDR),
         Paragraph('Equivalencia', S_TABLA_HDR)],
        [Paragraph('Matemáticas', S_TABLA_CELDA),
         Paragraph('5', S_TABLA_CELDA),
         Paragraph('5 × 40 min = 3h 20min por semana', S_TABLA_CELDA)],
        [Paragraph('Inglés', S_TABLA_CELDA),
         Paragraph('4', S_TABLA_CELDA),
         Paragraph('4 × 40 min = 2h 40min por semana', S_TABLA_CELDA)],
        [Paragraph('Mecanizado con Máquinas Herramienta', S_TABLA_CELDA),
         Paragraph('12', S_TABLA_CELDA),
         Paragraph('12 × 40 min = 8h por semana', S_TABLA_CELDA)],
    ]
    t = Table(lec_data, colWidths=[5.5*cm, 4*cm, 6*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  VERDE_OSCURO),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [white, GRIS_CLARO]),
        ('BOX',           (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    e.append(t)
    e.append(Spacer(1, 0.5*cm))

    # ── Bloques por sesión ──
    e.append(Paragraph('¿Qué son los Bloques por Sesión?', S_SUBSECCION))
    e.append(Paragraph(
        'El horario del CTP Heredia está dividido en <b>bloques de 3 lecciones consecutivas</b>: '
        'Bloque A (lecciones 1-3), Bloque B (4-6), Bloque C (7-9) y Bloque D (10-12). '
        'El campo <b>"Bloques por Sesión"</b> indica cuántos de estos bloques de 3 lecciones '
        'se imparten de forma continua en una sola sesión.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    bps_data = [
        [Paragraph('Bloques por Sesión', S_TABLA_HDR),
         Paragraph('Lecciones por sesión', S_TABLA_HDR),
         Paragraph('Ejemplo de uso', S_TABLA_HDR)],
        [Paragraph('1', S_TABLA_CELDA),
         Paragraph('3 lecciones continuas', S_TABLA_CELDA),
         Paragraph('Inglés, Matemáticas, Español', S_TABLA_CELDA)],
        [Paragraph('2', S_TABLA_CELDA),
         Paragraph('6 lecciones continuas', S_TABLA_CELDA),
         Paragraph('Mecanizado con Máquinas Herramienta,\nDibujo Arquitectónico', S_TABLA_CELDA)],
    ]
    t = Table(bps_data, colWidths=[4*cm, 4.5*cm, 7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  VERDE_OSCURO),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [white, GRIS_CLARO]),
        ('BOX',           (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    e.append(t)
    e.append(Spacer(1, 0.3*cm))

    e.append(caja_info(
        'Ejemplo: Mecanizado con Máquinas Herramienta tiene 12 lecciones semanales y '
        'Bloques por Sesión = 2. Esto significa que el sistema asignará sesiones de '
        '6 lecciones consecutivas (2 bloques × 3 lecciones), distribuyendo las 12 '
        'lecciones en 2 sesiones de 6 lecciones por semana.'))
    e.append(Spacer(1, 0.5*cm))

    # ── Materias por nivel ──
    e.append(PageBreak())
    e.append(Paragraph('Recomendación importante: materias con diferente carga por nivel',
                        S_SUBSECCION))
    e.append(Paragraph(
        'Es muy común que una misma materia tenga distinta cantidad de lecciones '
        'semanales según el nivel del grupo. En estos casos <b>se deben crear como '
        'materias separadas</b>, una por cada configuración diferente.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(caja_alerta(
        'Error frecuente — No crear materias separadas por nivel',
        'Si se ingresa Matemáticas con 3 lecciones y se asigna a los niveles 10°, 11° y 12°, '
        'pero en 12° deberían ser 4 lecciones, el sistema generará horarios incorrectos '
        'para los grupos de 12°. Siempre creá una materia diferente cuando cambia '
        'la cantidad de lecciones semanales o los bloques por sesión.'))
    e.append(Spacer(1, 0.4*cm))

    e.append(Paragraph('Ejemplo correcto:', S_SUBSECCION))
    ej_data = [
        [Paragraph('Materia a crear', S_TABLA_HDR),
         Paragraph('Lec. Semanales', S_TABLA_HDR),
         Paragraph('Bloques/Sesión', S_TABLA_HDR),
         Paragraph('Niveles', S_TABLA_HDR)],
        [Paragraph('Matemáticas 10°', S_TABLA_CELDA),
         Paragraph('3', S_TABLA_CELDA),
         Paragraph('1', S_TABLA_CELDA),
         Paragraph('10°', S_TABLA_CELDA)],
        [Paragraph('Matemáticas 11°', S_TABLA_CELDA),
         Paragraph('5', S_TABLA_CELDA),
         Paragraph('1', S_TABLA_CELDA),
         Paragraph('11°', S_TABLA_CELDA)],
        [Paragraph('Matemáticas 12°', S_TABLA_CELDA),
         Paragraph('4', S_TABLA_CELDA),
         Paragraph('1', S_TABLA_CELDA),
         Paragraph('12°', S_TABLA_CELDA)],
    ]
    t = Table(ej_data, colWidths=[5.5*cm, 3*cm, 3*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  VERDE_OSCURO),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [white, GRIS_CLARO]),
        ('BOX',           (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    e.append(t)
    e.append(Spacer(1, 0.5*cm))

    # ── Materias técnicas vs académicas ──
    e.append(Paragraph('Materias técnicas vs. materias académicas', S_SUBSECCION))
    e.append(Paragraph(
        'Esta distinción es fundamental para que el sistema asigne correctamente '
        'las materias a cada grupo:', S_CUERPO))
    e.append(Spacer(1, 0.2*cm))

    tipo_data = [
        [Paragraph('Tipo', S_TABLA_HDR),
         Paragraph('Especialidad', S_TABLA_HDR),
         Paragraph('Descripción', S_TABLA_HDR),
         Paragraph('Ejemplos', S_TABLA_HDR)],
        [Paragraph('Académica', S_TABLA_CELDA),
         Paragraph('Ninguna (dejar vacío)', S_TABLA_CELDA),
         Paragraph('Materias que reciben todos los grupos sin importar la especialidad.',
                   S_CAMPO_DESC),
         Paragraph('Matemáticas, Español, Inglés, Estudios Sociales, Ciencias', S_CAMPO_DESC)],
        [Paragraph('Técnica', S_TABLA_CELDA),
         Paragraph('Seleccionar la especialidad correspondiente', S_TABLA_CELDA),
         Paragraph('Materias exclusivas de una especialidad técnica. Solo se asignan a '
                   'grupos de esa especialidad.', S_CAMPO_DESC),
         Paragraph('Mecanizado (MP), Dibujo Arquitectónico (DT), Circuitos (ET)', S_CAMPO_DESC)],
    ]
    t = Table(tipo_data, colWidths=[2.5*cm, 3.5*cm, 5*cm, 4.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  VERDE_OSCURO),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [white, GRIS_CLARO]),
        ('BOX',           (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, GRIS_BORDE),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ]))
    e.append(t)
    e.append(Spacer(1, 0.4*cm))

    e.append(caja_nota(
        'Niveles en materias técnicas',
        'Las materias técnicas también deben tener los niveles correctamente asignados. '
        'Una materia técnica de 10° solo se asignará a grupos de 10° que pertenezcan '
        'a esa especialidad. Si una materia técnica aplica a los tres niveles, '
        'marcá 10°, 11° y 12°.'))
    e.append(Spacer(1, 0.4*cm))

    e.append(caja_nota(
        'Verificá antes de generar el horario',
        'Antes de generar el horario, revisá que: (1) cada materia tenga los niveles '
        'correctos marcados, (2) las materias técnicas tengan su especialidad asignada, '
        '(3) materias con diferente carga por nivel estén creadas por separado, '
        'y (4) la suma de lecciones semanales de todas las materias de un grupo no '
        'supere la capacidad del horario semanal (máximo 48 lecciones).'))
    return e


def seccion_horario():
    e = []
    e.append(PageBreak())
    e.append(encabezado_paso(5, 'Generación y Visualización del Horario'))
    e.append(Spacer(1, 0.4*cm))
    e.append(Paragraph(
        'Una vez ingresadas las especialidades, grupos, asignaciones y materias, '
        'el sistema puede generar el horario automáticamente usando un algoritmo '
        'de optimización con restricciones.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('Generación automática', S_SUBSECCION))
    e.append(lista(
        'En el menú lateral seleccioná <b>Horarios</b>.',
        'Indicá el <b>Año Lectivo</b> (ejemplo: 2026).',
        'Hacé clic en <b>"Generar Horario [año]"</b>.',
        'El sistema procesará todos los grupos simultáneamente. Esto puede tardar '
        'entre 30 segundos y varios minutos dependiendo de la cantidad de grupos.',
        'Al finalizar verás un mensaje de éxito con la cantidad de sesiones generadas.',
    ))
    e.append(Spacer(1, 0.3*cm))

    e.append(caja_nota(
        'El horario generado reemplaza el anterior',
        'Cada vez que se genera el horario, se elimina el horario automático existente '
        'para ese año lectivo. Los ajustes manuales que hayas hecho también se perderán. '
        'Hacé los ajustes manuales solo después de estar conforme con el horario base generado.'))
    e.append(Spacer(1, 0.4*cm))

    e.append(Paragraph('Visualización del horario', S_SUBSECCION))
    e.append(Paragraph(
        'Seleccioná un grupo en el selector para ver su horario semanal. '
        'Si el grupo tiene dos especialidades, aparecerán botones para cambiar '
        'entre las pistas de cada especialidad.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('Ajustes manuales', S_SUBSECCION))
    e.append(Paragraph(
        'Hacé clic sobre cualquier sesión en el horario para moverla a otro día o bloque. '
        'El sistema verificará automáticamente que no existan conflictos antes de guardar '
        'el cambio.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(Paragraph('Exportación', S_SUBSECCION))
    e.append(Paragraph(
        'Con el horario del grupo visible, usá los botones <b>PDF</b> o <b>Excel</b> '
        'para descargar el horario en el formato deseado.', S_CUERPO))
    e.append(Spacer(1, 0.3*cm))

    e.append(caja_info(
        'Si el sistema no encuentra solución para algún grupo, revisá que la suma '
        'de lecciones semanales no exceda la capacidad disponible y que todas las '
        'materias tengan los niveles y especialidades correctamente configurados.'))
    return e


# ── Pie de página dinámico ─────────────────────────────────────────

def pie_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRIS_TEXT)
    canvas.drawString(2*cm, 1.2*cm,
                      'CTP Heredia — Sistema de Gestión de Horarios  ·  Manual de Usuario')
    canvas.drawRightString(A4[0] - 2*cm, 1.2*cm, f'Página {doc.page}')
    canvas.setStrokeColor(GRIS_BORDE)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.6*cm, A4[0] - 2*cm, 1.6*cm)
    canvas.restoreState()


# ── Main ───────────────────────────────────────────────────────────

def generar():
    nombre = 'Manual_Usuario_Sistema_Horarios_CTP.pdf'
    doc = SimpleDocTemplate(
        nombre,
        pagesize=A4,
        leftMargin=2.5*cm,
        rightMargin=2.5*cm,
        topMargin=2.2*cm,
        bottomMargin=2.2*cm,
        title='Manual de Usuario — Sistema de Horarios CTP Heredia',
        author='CTP Heredia',
    )

    story = []
    story += portada()
    story += seccion_especialidades()
    story += seccion_grupos()
    story += seccion_asignacion()
    story += seccion_materias()
    story += seccion_horario()

    doc.build(story, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
    print(f'Manual generado: {nombre}')

if __name__ == '__main__':
    generar()
