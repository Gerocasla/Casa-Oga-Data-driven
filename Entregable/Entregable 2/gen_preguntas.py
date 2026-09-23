"""Genera el documento de preguntas de calidad de datos (ronda 2) para Casa Óga.
Criterio: preguntas abiertas. No se propone ninguna respuesta ni criterio provisorio:
la definicion la tiene que dar el negocio.
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "Preguntas-Calidad-de-Datos-Ronda-2.docx")

d = Document()
d.styles["Normal"].font.name = "Calibri"; d.styles["Normal"].font.size = Pt(10.5)
sec = d.sections[0]
sec.top_margin = sec.bottom_margin = Cm(2); sec.left_margin = sec.right_margin = Cm(2.2)

def H(txt, lvl=1):
    p = d.add_heading(txt, level=lvl)
    for r in p.runs: r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    return p

def par(txt, bold=False, italic=False, space=4):
    p = d.add_paragraph(); p.paragraph_format.space_after = Pt(space)
    r = p.add_run(txt); r.bold = bold; r.italic = italic
    return p

def bullets(items):
    for it in items:
        p = d.add_paragraph(style="List Bullet"); p.paragraph_format.space_after = Pt(2)
        if isinstance(it, tuple):
            r = p.add_run(it[0]); r.bold = True; p.add_run(it[1])
        else:
            p.add_run(it)

def tabla(headers, rows, widths=None):
    t = d.add_table(rows=1, cols=len(headers)); t.style = "Light Grid Accent 1"
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9.5)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(val)); r.font.size = Pt(9.5)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

N = [0]
def pregunta(txt):
    N[0] += 1
    p = d.add_paragraph(); p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(3)
    r = p.add_run(f"P{N[0]}. "); r.bold = True; r.font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)
    r2 = p.add_run(txt); r2.bold = True
    resp = d.add_paragraph(); resp.paragraph_format.space_after = Pt(8)
    rr = resp.add_run("Respuesta: "); rr.italic = True; rr.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    rs = resp.add_run("_" * 78); rs.font.color.rgb = RGBColor(0xBF, 0xBF, 0xBF)

# ---------------------------------------------------------------- portada
t = d.add_heading("Casa Óga — Preguntas abiertas de calidad de datos (Ronda 2)", level=0)
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
par("Proyecto Data Driven · Grupo 1 · Entregable 2 — Evaluación de calidad de datos", italic=True).alignment = WD_ALIGN_PARAGRAPH.CENTER
par("")
tabla(["Campo", "Detalle"],
      [["Origen de las preguntas", "Análisis exploratorio y de calidad sobre los 15 datasets recibidos (período enero 2022 a agosto 2026)."],
       ["Destinatarios sugeridos", "Compras y Categorías, Dirección Financiera, Dirección Comercial, Sistemas / referente técnico de Operaciones."],
       ["Fecha de envío", "[completar]"],
       ["Fecha solicitada de respuesta", "[completar]"],
       ["Respondido por", "[completar]"]], widths=[5.0, 11.5])
par("Cada bloque empieza con lo que encontramos en los datos y sigue con las preguntas. "
    "No proponemos respuestas: necesitamos el criterio de ustedes para poder aplicarlo. "
    "Las preguntas están numeradas para facilitar la respuesta punto por punto, por escrito o en una reunión.", italic=True)

# ---------------------------------------------------------------- BLOQUE 1
H("Bloque 1 · Productos sin costo unitario en el catálogo (22 SKUs)", 1)
par("Qué encontramos en los datos", bold=True)
bullets([
    ("22 de 800 productos (2,7%) no tienen cargado el costo unitario", " en el catálogo. El precio de lista sí está cargado en los 22."),
    ("Los 22 son altas recientes: ", "sus fechas de alta van del 6 de febrero al 27 de junio de 2025. Ningún producto anterior a 2025 tiene el costo vacío."),
    ("16 siguen activos y 6 fueron discontinuados.", " Entre todos suman 2.610 unidades en stock, repartidas en 192 combinaciones de producto y tienda."),
    ("Acumulan $235,7 millones de venta", " en el período analizado."),
    ("Esos mismos 22 productos sí tienen costo cargado en sus órdenes de compra", " (entre 1 y 9 órdenes cada uno)."),
    ("Tomando el costo de esas órdenes de compra, ", "el margen sobre precio de lista de estos 22 productos daría entre 52% y 58%, mientras que el resto del catálogo tiene un margen promedio de 45%."),
])
par("Por qué lo preguntamos", bold=True)
par("El capital inmovilizado se calcula valuando el stock a costo. Sin ese dato, estos productos quedan fuera de la medición.")
pregunta("¿Cuál es el circuito de carga del costo unitario de un producto nuevo? ¿Qué área lo carga y en qué momento del alta?")
pregunta("¿Qué explica que estos 22 productos, todos dados de alta en 2025, hayan quedado sin costo?")
pregunta("¿Qué incluye exactamente el costo unitario del catálogo? ¿Es el precio de compra al proveedor, o incorpora otros componentes como flete, impuestos o nacionalización?")
pregunta("¿Es el mismo concepto que el costo unitario que figura en las órdenes de compra? Si no lo es, ¿en qué se diferencian?")
pregunta("¿De qué fuente debemos tomar el costo de estos 22 productos?")
pregunta("¿Quién puede entregarnos ese dato y en qué plazo?")
pregunta("Mientras tanto, ¿cómo quieren que tratemos a estos 22 productos en los cálculos de capital inmovilizado y de margen?")
par("Listado de los 22 productos: archivo adjunto “skus_sin_costo.csv”.", italic=True)

# ---------------------------------------------------------------- BLOQUE 2
d.add_page_break()
H("Bloque 2 · Costo unitario vacío en el historial de precios", 1)
par("Qué encontramos en los datos", bold=True)
bullets([
    ("40 registros del historial de precios no tienen costo unitario", ", y corresponden exactamente a los mismos 22 productos del bloque anterior."),
    ("El vacío es total por producto: ", "ninguno de los 22 tiene costo cargado en una vigencia y vacío en otra."),
    ("En esos 40 registros el precio de lista sí está cargado.", " Falta únicamente el costo."),
    ("El resto del historial es consistente: ", "no hay vigencias solapadas ni períodos sin cubrir, la última vigencia de cada producto coincide con el precio del catálogo en los 800 casos, y la primera coincide con la fecha de alta en los 800."),
    ("Entre una vigencia y la siguiente, ", "el precio de lista sube 86% en la mediana, con casos de hasta 393%."),
])
pregunta("¿Cuál de los dos sistemas es la fuente maestra del costo: el catálogo de productos o el historial de precios? Si los valores difieren, ¿cuál debe prevalecer?")
pregunta("¿Cómo se alimenta el historial de precios? ¿Se genera a partir del catálogo o son cargas independientes?")
pregunta("Cuando cambia el costo de un producto, ¿qué se registra? ¿Se abre una vigencia nueva o se actualiza el valor existente?")
pregunta("Cuando un producto se compra a más de un proveedor con costos distintos, ¿cómo se registra esa situación? Lo consultamos porque hay 15 productos que figuran en el catálogo con dos proveedores, y el historial guarda un único costo por producto y vigencia.")
pregunta("¿A qué responden las variaciones de precio entre vigencias? ¿Siguen algún criterio de actualización definido?")
pregunta("¿Los análisis de venta y de margen deben hacerse a precios corrientes de cada período, o hay una referencia que la empresa use para comparar valores entre años?")

# ---------------------------------------------------------------- BLOQUE 3
d.add_page_break()
H("Bloque 3 · Valores que no pueden existir por definición", 1)
par("Encontramos 5.854 registros con valores que contradicen la naturaleza de la variable. No son valores extremos "
    "discutibles: son datos imposibles, como un stock negativo.")
tabla(["Caso", "Registros", "Rango del problema", "Fuente"],
      [["Stock disponible negativo", "1.209", "hasta −152 unidades", "Stock por SKU, tienda y mes"],
       ["Unidades vendidas negativas", "2.317", "hasta −26 unidades", "Ventas por SKU, tienda y mes"],
       ["Venta neta negativa", "2.317", "hasta −$1.705.312", "Ventas por SKU, tienda y mes"],
       ["Descuento fuera del rango 0-100%", "3", "120%, 120% y −10%", "Liquidaciones"],
       ["Descuento fuera del rango 0-100%", "2", "150% y −15%", "Promociones comerciales"],
       ["Presupuesto o unidades negativas", "6", "hasta −$963.369 y −9 unidades", "Presupuesto de ventas"]],
      widths=[6.5, 2.2, 5.3, 5.5])

H("3.1 Stock disponible negativo (1.209 registros)", 2)
par("Qué encontramos en los datos", bold=True)
bullets([
    ("Está repartido, no concentrado: ", "afecta a 548 productos, a las 28 tiendas y a 1.117 combinaciones distintas de producto y tienda."),
    ("Aumenta a lo largo del tiempo: ", "67 casos en 2022, 255 en 2023, 394 en 2024 y 493 en 2025."),
    ("Los valores son chicos: ", "la mediana es de −11 unidades y solo 5 registros superan las 100 unidades."),
    ("El 81,6% de esos registros tuvo ventas ese mismo mes", " y el tamaño del faltante acompaña a las unidades vendidas."),
    ("En 1.148 de los 1.209 casos, ", "el mes siguiente esa misma combinación vuelve a tener stock positivo."),
])
pregunta("¿Qué representa un stock negativo en el reporte? ¿A qué situación operativa corresponde?")
pregunta("¿Existe algún proceso de conteo o ajuste posterior que corrija estos casos? Si existe, ¿podemos recibir esos ajustes?")
pregunta("¿Cómo quieren que tratemos estos registros en el análisis?")
pregunta("¿Hay algún control previsto para evitar que el stock quede en negativo?")

H("3.2 Unidades y venta neta negativas (2.317 registros)", 2)
par("Qué encontramos en los datos", bold=True)
bullets([
    ("Los 2.317 registros negativos de venta coinciden uno a uno con los 2.317 registros del dataset de devoluciones", ": misma tienda, mismo producto, mismo mes y las mismas unidades."),
    ("Representan 9.583 unidades, ", "el 1,27% de las unidades vendidas en el período."),
    ("Por motivo de devolución: ", "producto dañado en logística 499 casos, producto sin rotación o no vendido 471, devolución de cliente por cambio 466, error de picking 446 y defecto de fabricación 435."),
    ("En solo 40 de los 2.317 casos ", "existe además un registro de venta positiva del mismo producto, tienda y mes."),
])
pregunta("¿Qué operación hay detrás de cada uno de los cinco motivos de devolución? Nos interesa entender en particular qué significa “producto sin rotación / no vendido”.")
pregunta("¿Todos esos motivos se registran como una venta negativa en el sistema, o algunos deberían ser movimientos de inventario?")
pregunta("¿La venta neta que figura en el reporte ya tiene descontadas las devoluciones, o el reporte las presenta como un registro separado?")
pregunta("Cuando se devuelve una unidad, ¿qué sucede físicamente con ella? ¿Vuelve al stock vendible de la tienda, se da de baja o se devuelve al proveedor?")
pregunta("¿Existe la posibilidad de devolverle mercadería sin rotación al proveedor? Si existe, ¿bajo qué condiciones y con qué proveedores?")
pregunta("¿Cómo quieren que tratemos estos registros al calcular el ritmo de venta de cada producto?")

H("3.3 Descuentos fuera del rango 0-100% (5 registros)", 2)
tabla(["Registro", "Producto / Categoría", "Tienda", "Fecha", "Descuento", "Motivo"],
      [["LIQ0077", "SKU00150", "T11", "11-dic-2023", "120%", "Fin de temporada"],
       ["LIQ0477", "SKU00236", "T27", "26-sep-2025", "120%", "Discontinuación"],
       ["LIQ0306", "SKU00308", "T27", "09-dic-2025", "−10%", "Baja rotación"],
       ["PROMO0052", "Textil hogar (Online)", "—", "15-dic-2023", "150%", "Navidad"],
       ["PROMO0072", "Baño (Online)", "—", "03-jun-2022", "−15%", "—"]],
      widths=[2.8, 4.6, 1.8, 2.8, 2.2, 3.3])
par("Dato de contexto: el resto de los descuentos toma solo valores redondos. En liquidaciones, de 10% a 50%; "
    "en promociones, de 5% a 40%.")
pregunta("¿Qué significa un descuento de 120% o de 150%? ¿Corresponde a algún tipo de acción comercial?")
pregunta("¿Y un descuento negativo, como −10% o −15%?")
pregunta("¿Cuál es el rango válido de descuento según la política comercial? ¿Quién lo autoriza?")
pregunta("¿El sistema valida el valor del descuento al momento de la carga?")
pregunta("¿Cómo quieren que tratemos estos 5 registros en el análisis de margen?")

H("3.4 Presupuesto con valores negativos o en cero", 2)
tabla(["Mes", "Tienda", "Categoría", "Presupuesto $", "Presupuesto unidades"],
      [["jun-2022", "T07", "Textil hogar", "33.895", "−2"],
       ["jun-2022", "T22", "Baño", "−6.596", "4"],
       ["jul-2022", "T17", "Iluminación", "−963.369", "−9"],
       ["ene-2023", "T24", "Iluminación", "−514.763", "14"],
       ["may-2023", "T10", "Organización", "359.860", "−4"]],
      widths=[2.6, 2.2, 3.4, 3.6, 4.2])
par("Además hay 309 celdas con presupuesto en cero, todas entre enero y mayo de 2022 y repartidas en las 28 tiendas. "
    "Como referencia, el presupuesto promedio de una celda en 2022 es de $850.428.")
pregunta("¿Qué significa un presupuesto negativo? ¿Corresponde a un ajuste o corrección sobre otro período?")
pregunta("¿Y un presupuesto en cero? ¿Significa que no se asignó meta para ese mes, o que el dato no llegó a cargarse?")
pregunta("¿Cómo se construye el presupuesto de ventas y quién lo aprueba?")
pregunta("¿Cómo quieren que tratemos estos registros al medir el cumplimiento contra presupuesto?")

# ---------------------------------------------------------------- cierre
d.add_page_break()
H("Resumen de lo que necesitamos definir", 1)
tabla(["Tema", "Preguntas", "Área que puede responder", "Impacto si no se define"],
      [["Costo de 22 productos", "P1 a P7", "Compras y Categorías · Finanzas", "No se puede valuar el capital inmovilizado de esos productos"],
       ["Fuente maestra del costo", "P8 a P13", "Finanzas · Sistemas", "Cálculo de margen y de capital a costo"],
       ["Stock negativo", "P14 a P17", "Sistemas · Operaciones", "Cálculo de cobertura y de meses de stock"],
       ["Devoluciones", "P18 a P23", "Operaciones · Comercial", "Definición de la variable que va a predecir el modelo"],
       ["Descuentos fuera de rango", "P24 a P28", "Comercial", "Análisis de margen en liquidaciones"],
       ["Presupuesto", "P29 a P32", "Finanzas · Comercial", "Indicador de desvío contra presupuesto"]],
      widths=[3.6, 2.6, 4.4, 6.4])
par("")
par("Los cuatro primeros temas son necesarios para avanzar con la etapa de modelado. Los dos últimos tienen un "
    "impacto acotado y pueden resolverse en paralelo.", italic=True)
par("")
par("Quedamos a disposición para coordinar una reunión si resulta más práctico que responder por escrito.", italic=True)

d.save(OUT)
print("OK ->", OUT, "| preguntas:", N[0])
