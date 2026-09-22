"""Genera el documento de preguntas de calidad de datos (ronda 2) para Casa Óga."""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "Preguntas-Calidad-de-Datos-Ronda-2.docx")

d = Document()
for st, sz in [("Normal", 10.5)]:
    d.styles[st].font.name = "Calibri"; d.styles[st].font.size = Pt(sz)
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

def bullets(items, style="List Bullet"):
    for it in items:
        p = d.add_paragraph(style=style); p.paragraph_format.space_after = Pt(2)
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

def pregunta(n, txt):
    p = d.add_paragraph(); p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(3)
    r = p.add_run(f"P{n}. "); r.bold = True; r.font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)
    r2 = p.add_run(txt); r2.bold = True

# ---------------------------------------------------------------- portada
t = d.add_heading("Casa Óga — Preguntas abiertas de calidad de datos (Ronda 2)", level=0)
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
par("Proyecto Data Driven · Grupo 1 · Entregable 2 — Evaluación de calidad de datos", italic=True).alignment = WD_ALIGN_PARAGRAPH.CENTER
par("")
tabla(["Campo", "Detalle"],
      [["Origen de las preguntas", "Análisis exploratorio y de calidad sobre los 15 datasets recibidos (período ene-2022 a dic-2025)."],
       ["Destinatarios sugeridos", "Compras y Categorías (Diego P.), Dirección Financiera (Carlos F.), Dirección Comercial (María G.), Sistemas / referente técnico de Operaciones."],
       ["Fecha", "[completar]"],
       ["Respuestas", "[completar]"]], widths=[4.5, 12])
par("Cada punto indica qué se detectó, por qué importa para el proyecto y qué criterio aplicaríamos si no hubiera respuesta. "
    "Los criterios provisorios están marcados como tales: no son decisiones tomadas.", italic=True)

# ---------------------------------------------------------------- BLOQUE 1
H("Bloque 1 · Productos sin costo unitario en el catálogo (22 SKUs)", 1)
par("Qué se detectó", bold=True)
bullets([
    ("22 de 800 SKUs (2,7%) no tienen cargado el costo unitario", " en Productos_catalogo.csv. Sí tienen precio de lista."),
    ("Los 22 son altas recientes: ", "todas sus fechas de alta están entre el 6-feb-2025 y el 27-jun-2025. Ningún SKU anterior a 2025 tiene el costo vacío."),
    ("16 siguen activos y 6 fueron discontinuados. ", "A dic-2025 tienen 2.610 unidades en stock repartidas en 192 posiciones SKU-tienda."),
    ("Representan $235,7 M de venta acumulada (0,73% del total)", ", pero su stock no se puede valuar a costo, que es la base del cálculo de capital inmovilizado."),
    ("Los 22 SKUs sí tienen órdenes de compra con costo cargado", " (entre 1 y 9 OC cada uno). El costo promedio ponderado por unidades va de $4.718 a $38.504."),
])
par("Por qué importa", bold=True)
par("El capital inmovilizado —la cifra central del proyecto— se calcula valuando el stock a costo. Hoy estos SKUs quedan fuera de esa "
    "valuación o se estiman. En el Entregable 1 se imputaron con la mediana de costo de su categoría; comparado contra el costo real de "
    "las órdenes de compra, esa estimación se desvía un 11,9% en la mediana, con casos de −84% y +63%.")
par("Un dato que no cierra y necesita explicación", bold=True)
par("Si se usara el costo de las órdenes de compra, estos 22 productos tendrían un margen sobre precio de lista de 52% a 58% "
    "(mediana 55,2%), muy por encima del 45,4% del resto del catálogo. O son productos genuinamente más rentables, o el costo de la "
    "orden de compra y el costo del catálogo no son la misma magnitud (por ejemplo, si el del catálogo incluye flete, impuestos o "
    "costos de importación que la OC no tiene).")
pregunta(1, "¿Por qué quedaron sin costo justamente los productos dados de alta en 2025? ¿Cambió el circuito de carga de productos nuevos ese año?")
pregunta(2, "¿Quién es hoy el responsable de cargar el costo unitario de un producto nuevo, y en qué momento del alta debería quedar cargado?")
pregunta(3, "¿El costo_unitario del catálogo es el mismo concepto que el costo_unitario_ars de una orden de compra, o el del catálogo incluye componentes adicionales (flete, impuestos, nacionalización)? Esto define si podemos completar los faltantes desde las órdenes de compra.")
pregunta(4, "Si podemos usar las órdenes de compra: ¿qué criterio prefieren, el costo de la última orden, el promedio ponderado por unidades, o un costo de reposición que ustedes definan?")
pregunta(5, "¿Pueden entregar directamente el costo de estos 22 SKUs desde el sistema de Compras? Es la opción preferible: evita cualquier estimación.")
par("Criterio provisorio si no hay respuesta: ", bold=True)
par("se valúa con el costo promedio ponderado de las órdenes de compra de cada SKU y se marca la fila como costo estimado, para poder "
    "recalcular después. Con ese criterio el stock de estos SKUs vale $67,1 M a dic-2025.", space=10)
par("Detalle de los 22 SKUs: archivo Entregable 2/EDA/resultados/skus_sin_costo.csv", italic=True)

# ---------------------------------------------------------------- BLOQUE 2
d.add_page_break()
H("Bloque 2 · Costo unitario vacío en el historial de precios", 1)
par("Qué se detectó", bold=True)
bullets([
    ("40 filas de Historial_Precios_SKU.csv no tienen costo unitario", ", y corresponden exactamente a los mismos 22 SKUs del Bloque 1."),
    ("El vacío es total por producto: ", "ninguno de los 22 tiene costo en una vigencia y vacío en otra. O está en todas, o en ninguna."),
    ("El precio de lista sí está cargado en las 40 filas.", " Falta únicamente el costo."),
    ("El resto del historial es consistente: ", "sin solapamientos ni huecos entre vigencias, la última vigencia coincide con el precio del catálogo en los 800 SKUs, y la primera coincide con la fecha de alta en los 800."),
])
par("Por qué importa", bold=True)
par("Confirma que el problema está en el alta del producto y no en el mantenimiento de precios: el costo nunca entró al sistema. "
    "También implica que no se puede reconstruir el costo histórico de estos SKUs, ni calcular su margen real en liquidaciones.")
pregunta(6, "¿Cuál es la fuente maestra del costo: el catálogo de productos o el historial de precios? ¿Cuál manda si difieren?")
pregunta(7, "¿El historial de precios se alimenta automáticamente del catálogo, o son cargas independientes? Lo preguntamos porque el vacío es idéntico en ambos, lo que sugiere una única fuente o una réplica.")
pregunta(8, "Cuando un producto cambia de proveedor y de costo, ¿se registra una nueva vigencia en el historial o se pisa el valor anterior?")
pregunta(9, "Para los 15 SKUs que aparecen duplicados en el catálogo con dos proveedores distintos: ¿el costo debería ser uno por proveedor? Hoy el historial guarda un solo costo por SKU y por vigencia, así que el modelo de datos no contempla ese caso.")
par("Observación adicional para validar", bold=True)
par("Entre vigencias consecutivas, el precio de lista sube 86% en la mediana y hasta 393%. Son saltos nominales grandes: hace falta "
    "confirmar si responden a la inflación del período, para decidir si el análisis se hace a precios corrientes o constantes.", space=10)

# ---------------------------------------------------------------- BLOQUE 3
d.add_page_break()
H("Bloque 3 · Valores imposibles detectados (5.854 registros)", 1)
par("Se agrupan acá todos los valores que no pueden existir por definición. No son valores extremos discutibles: son datos que "
    "contradicen la naturaleza de la variable.")
tabla(["Caso", "Registros", "Rango del problema", "Fuente"],
      [["Stock disponible negativo", "1.209", "hasta −152 unidades", "Stock_SKU_tienda_mensual"],
       ["Unidades vendidas negativas", "2.317", "hasta −26 unidades", "Ventas_SKU_tienda_mensual"],
       ["Venta neta negativa", "2.317", "hasta −$1.705.312", "Ventas_SKU_tienda_mensual"],
       ["Descuento fuera de 0-100%", "3", "120%, 120% y −10%", "Liquidaciones"],
       ["Descuento fuera de 0-100%", "2", "150% y −15%", "Promociones_Comerciales"],
       ["Presupuesto o unidades negativas", "6", "hasta −$963.369 y −9 unidades", "Presupuesto_Ventas"]],
      widths=[6.5, 2.2, 5.3, 5.5])

H("3.1 Stock negativo (1.209 filas)", 2)
par("Qué encontramos", bold=True)
bullets([
    ("Está repartido, no concentrado: ", "548 SKUs, las 28 tiendas, 1.117 posiciones distintas. La tienda más afectada tiene 58 casos."),
    ("Crece con el negocio: ", "67 casos en 2022, 255 en 2023, 394 en 2024 y 493 en 2025."),
    ("Es chico en magnitud: ", "mediana −11 unidades; solo 5 filas superan las 100 unidades."),
    ("Respalda la explicación de sincronización POS-inventario que dio el negocio: ", "el 81,6% de esas filas tuvo ventas ese mes, el faltante se correlaciona con las unidades vendidas (0,75) y en 1.148 de 1.209 casos el mes siguiente vuelve a stock positivo."),
])
pregunta(10, "¿Confirman que el stock negativo es un desfasaje de sincronización entre el POS y el sistema de inventario, y no un ajuste de inventario real?")
pregunta(11, "¿Llevarlo a cero es el tratamiento correcto, o prefieren que lo reconstruyamos como “stock inicial menos ventas” del mes?")
pregunta(12, "¿Hay algún proceso de conteo o ajuste que corrija estos casos más adelante? Si existe, ¿podemos recibir esos ajustes?")
par("Criterio provisorio: ", bold=True)
par("se lleva a 0 y se marca la fila con una columna de auditoría. Impacto acotado: son 20.914 unidades sobre un stock que a "
    "dic-2025 es de 135.484.", space=8)

H("3.2 Unidades y venta neta negativas (2.317 filas)", 2)
par("Qué encontramos", bold=True)
bullets([
    ("Son exactamente las devoluciones. ", "Las 2.317 filas negativas coinciden una a una con los 2.317 registros de Devoluciones_SKU.csv: misma tienda, mismo SKU, mismo mes y las mismas unidades. Ya no es una hipótesis."),
    ("Pesan poco: ", "9.583 unidades, el 1,27% de las unidades vendidas; $418,3 M en valor absoluto."),
    ("Pero los motivos no coinciden con lo que se nos informó. ", "En el Entregable 1 el negocio indicó que eran “mayormente devoluciones de clientes”. En el dataset solo 466 de 2.317 (20%) son “Devolución de cliente (cambio)”. El resto es producto dañado en logística (499), producto sin rotación / no vendido (471), error de picking (446) y defecto de fabricación (435)."),
    ("En solo 40 de los 2.317 casos ", "hay además una fila de venta positiva del mismo producto, tienda y mes."),
])
pregunta(13, "El dataset de devoluciones muestra que solo el 20% son devoluciones de clientes. ¿Los otros cuatro motivos (daño en logística, error de picking, defecto de fábrica, producto sin rotación) también se registran como venta negativa en el POS, o deberían ser movimientos de inventario?")
pregunta(14, "“Producto sin rotación / no vendido” (471 registros, 2.013 unidades) — ¿qué operación representa? ¿Es una devolución al proveedor? Es directamente relevante para el proyecto: si se puede devolver mercadería sin rotación, es una palanca de acción que hoy no estamos contemplando.")
pregunta(15, "¿La venta neta ya tiene descontadas las devoluciones, o hay que restarlas aparte? Con la coincidencia uno a uno, la lectura es que la devolución está cargada como una fila negativa separada.")
pregunta(16, "Para el modelo: cuando un producto se devuelve por daño o defecto, ¿la unidad vuelve al stock vendible de la tienda o se da de baja?")
par("Criterio provisorio: ", bold=True)
par("se dejan de llevar a cero. Se separan como devoluciones y se netean de la venta del mes para calcular el ritmo de rotación, "
    "conservando el motivo como variable.", space=8)

H("3.3 Descuentos fuera de rango (5 registros)", 2)
tabla(["Registro", "Producto / Categoría", "Tienda", "Fecha", "Descuento", "Motivo"],
      [["LIQ0077", "SKU00150", "T11", "11-dic-2023", "120%", "Fin de temporada"],
       ["LIQ0477", "SKU00236", "T27", "26-sep-2025", "120%", "Discontinuación"],
       ["LIQ0306", "SKU00308", "T27", "09-dic-2025", "−10%", "Baja rotación"],
       ["PROMO0052", "Textil hogar (Online)", "—", "15-dic-2023", "150%", "Navidad"],
       ["PROMO0072", "Baño (Online)", "—", "03-jun-2022", "−15%", "—"]],
      widths=[2.8, 4.6, 1.8, 2.8, 2.2, 3.3])
par("Contexto útil: ", bold=True)
par("el resto de los descuentos usa solo valores redondos. En liquidaciones son 10, 15, 20, 25, 30, 40 y 50%. En promociones, de 5 a 40%. "
    "Los cinco casos son los únicos fuera de ese patrón, lo que sugiere error de carga y no una política excepcional.")
pregunta(17, "Los dos descuentos de 120% y el de 150%: ¿son errores de tipeo (por ejemplo 20% y 50%), o hubo alguna acción de bonificación total? Un descuento mayor a 100% implicaría pagarle al cliente por llevarse el producto.")
pregunta(18, "Los descuentos negativos (−10% y −15%): ¿significan un recargo, o son también un error de carga?")
pregunta(19, "¿El sistema valida el rango del descuento al cargarlo? Si no lo valida, conviene incluirlo en el plan de mejora de calidad de datos.")
par("Criterio provisorio: ", bold=True)
par("se excluyen los 5 registros de los cálculos de margen y se marcan, en lugar de acotarlos a 0-100% como se hizo en el "
    "Entregable 1. Acotar inventa un valor que nadie confirmó.", space=8)

H("3.4 Presupuesto negativo (6 valores en 5 filas)", 2)
tabla(["Mes", "Tienda", "Categoría", "Presupuesto $", "Presupuesto unidades"],
      [["jun-2022", "T07", "Textil hogar", "33.895", "−2"],
       ["jun-2022", "T22", "Baño", "−6.596", "4"],
       ["jul-2022", "T17", "Iluminación", "−963.369", "−9"],
       ["ene-2023", "T24", "Iluminación", "−514.763", "14"],
       ["may-2023", "T10", "Organización", "359.860", "−4"]],
      widths=[2.6, 2.2, 3.4, 3.6, 4.2])
par("Se suma un caso relacionado: ", bold=True)
par("309 celdas con presupuesto en cero, todas entre enero y mayo de 2022, en las 28 tiendas. El presupuesto promedio de una celda "
    "en 2022 es de $850.428, así que un cero no parece una meta real sino una carga pendiente.")
pregunta(20, "¿Un presupuesto negativo tiene algún significado (por ejemplo, un ajuste o una corrección contra un mes anterior), o son errores de carga?")
pregunta(21, "Los 309 ceros de enero a mayo 2022: ¿son meses sin presupuesto asignado o es información que no llegó a cargarse? Cambia si los tomamos como meta cero o los excluimos del cálculo de cumplimiento.")
pregunta(22, "¿Cómo se arma el presupuesto y quién lo aprueba? Lo consultamos porque el cumplimiento da un valor casi idéntico —alrededor del 91%— en todos los años, categorías y tiendas, lo que es llamativamente parejo para una meta comercial.")
par("Criterio provisorio: ", bold=True)
par("se excluyen las 5 filas negativas y los 309 ceros del cálculo de cumplimiento, y se documenta la exclusión.", space=8)

# ---------------------------------------------------------------- cierre
d.add_page_break()
H("Resumen de lo que necesitamos", 1)
tabla(["Tema", "Qué pedimos", "Responsable sugerido", "Bloquea"],
      [["Costo de 22 SKUs", "Costo unitario real desde el sistema de Compras, o confirmar que podemos usar el de las órdenes de compra",
        "Compras y Categorías · Finanzas", "Valuación del capital inmovilizado"],
       ["Definición de costo", "Si el costo del catálogo y el de la orden de compra son el mismo concepto", "Finanzas", "Cálculo de margen y de capital"],
       ["Stock negativo", "Confirmar el origen y el tratamiento", "Sistemas · Operaciones", "Cálculo de cobertura"],
       ["Devoluciones", "Qué operación hay detrás de cada motivo y si la unidad vuelve al stock", "Operaciones · Comercial", "Variable objetivo del modelo"],
       ["Descuentos fuera de rango", "Confirmar si son errores de carga", "Comercial", "Análisis de margen (impacto menor)"],
       ["Presupuesto", "Sentido de los negativos y de los ceros de 2022", "Finanzas · Comercial", "KPI de desvío contra presupuesto"]],
      widths=[3.6, 6.4, 3.6, 3.4])
par("")
par("Los cuatro primeros son bloqueantes para la fase de modelado. Los dos últimos tienen impacto acotado y pueden resolverse en "
    "paralelo.", italic=True)

d.save(OUT)
print("OK ->", OUT)
