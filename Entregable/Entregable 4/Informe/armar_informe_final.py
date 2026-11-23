"""Entregable 4 - final consolidated report (Entregables 1 to 3 with every correction applied).

Builds  Entregable 4/Casa_Oga_Informe_Final_Grupo_1.docx  with python-docx.
Numbers of the model and the economics come from Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json
(run modelo_final_v4.py first) and the charts from graficos_informe.py.
Run from the repo root:  python "Entregable/Entregable 4/Informe/armar_informe_final.py"
"""
import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT  # noqa: F401
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTDOC = HERE.parent / "Casa_Oga_Informe_Final_Grupo_1.docx"
R = json.loads((ROOT / "Entregable/Entregable 4/Modelo/resultados/modelo_final_v4_resultados.json").read_text(encoding="utf-8"))
G = HERE / "graficos"
DB = json.loads((ROOT / "Entregable/Entregable 4/Dashboard/datos_dashboard.json").read_text(encoding="utf-8"))

ACCENT = RGBColor(0x1F, 0x4E, 0x79)
INK2 = RGBColor(0x52, 0x51, 0x4E)
HEAD_FILL, BOX_FILL = "1F4E79", "EAF1F8"


def pct(x, d=1):
    return f"{100 * x:.{d}f}%".replace(".", ",")


def num(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def usd(x):
    return "USD " + num(x)


# ------------------------------------------------------------------ document helpers
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Cm(2.2))
sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(2.0)

st = doc.styles["Normal"]
st.font.name, st.font.size = "Calibri", Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(5)
st.paragraph_format.line_spacing = 1.1
for lvl, size, before in ((1, 15, 16), (2, 12, 10), (3, 11, 8)):
    h = doc.styles[f"Heading {lvl}"]
    h.font.name, h.font.size, h.font.bold = "Calibri", Pt(size), True
    h.font.color.rgb = ACCENT
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    h.paragraph_format.space_before, h.paragraph_format.space_after = Pt(before), Pt(4)
    h.paragraph_format.keep_with_next = True

# footer: page number
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = fp.add_run("Casa Óga · Informe final · Grupo 1 · pág. ")
r.font.size, r.font.color.rgb = Pt(8), INK2
for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
    if t:
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), t)
    else:
        el = OxmlElement("w:instrText")
        el.set(qn("xml:space"), "preserve")
        el.text = txt
    run = fp.add_run()
    run.font.size = Pt(8)
    run._r.append(el)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), fill)
    tcPr.append(sh)


def rich(par, text, size=None, color=None, bold_all=False):
    """**bold** markup inside a run sequence."""
    parts = text.replace("`", "").split("**")
    for i, part in enumerate(parts):
        if not part:
            continue
        run = par.add_run(part)
        run.bold = bold_all or i % 2 == 1
        if size:
            run.font.size = Pt(size)
        if color:
            run.font.color.rgb = color
    return par


def H(text, lvl=1):
    return doc.add_heading(text, lvl)


def P(text, size=None, after=None, italic=False, color=None, align=None):
    p = doc.add_paragraph()
    rich(p, text, size, color)
    if italic:
        for run in p.runs:
            run.italic = True
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if align:
        p.alignment = align
    return p


def B(items, style="List Bullet"):
    for it in items:
        p = doc.add_paragraph(style=style)
        rich(p, it)
        p.paragraph_format.space_after = Pt(2)


def T(header, rows, widths=None, size=9, first_bold=False):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        rich(c.paragraphs[0], h, size, RGBColor(0xFF, 0xFF, 0xFF), bold_all=True)
        shade(c, HEAD_FILL)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            rich(cells[i].paragraphs[0], str(v), size, bold_all=first_bold and i == 0)
    # repeat header row
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(1)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def BOX(title, text):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    c = t.rows[0].cells[0]
    shade(c, BOX_FILL)
    c.text = ""
    rich(c.paragraphs[0], title, 10, ACCENT, bold_all=True)
    for para in text if isinstance(text, list) else [text]:
        rich(c.add_paragraph(), para, 9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def IMG(path, caption, width=16.4):
    doc.add_picture(str(path), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    P(caption, 8.5, after=8, italic=True, color=INK2, align=WD_ALIGN_PARAGRAPH.CENTER)


def BREAK():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ------------------------------------------------------------------ numbers from the results
pv, pt_, ptr = R["periodos"]["validacion"], R["periodos"]["test"], R["periodos"]["train"]
fv, ft = R["flujo"]["validacion"], R["flujo"]["test"]
rv, rt = R["roi"]["validacion"], R["roi"]["test"]
vb, ve1 = R["insumos"]["valor_unitario"]["base_e2"], R["insumos"]["valor_unitario"]["sensibilidad_e1"]
vi = R["validacion_interna"]
DB_AL = DB["alertas"]
DB_N = len(DB_AL)
DB_MES = "agosto de 2026" if DB["mes_lista"] == "2026-08" else DB["mes_lista"]
DB_A = sum(a["bloque"] == "A" for a in DB_AL)
DB_IN = [a for a in DB_AL if a["dentro_capacidad"]]
DB_CAP = sum(a["capital_ars"] for a in DB_AL)
DB_CAP_IN = sum(a["capital_ars"] for a in DB_IN)
DB_ACC = {k: sum(a["accion"] == k for a in DB_AL) for k in ("Transferir", "Liquidar", "Frenar compra", "Frenar reposición")}
kb = R["punto_operacion"]["k_bloque_b"]
pers = R["persistencia_sin_venta"]
imp = R["importancia_permutacion"]
seg = R["segmentos"]
c = lambda per, k, m: R["periodos"][per]["curva"][str(k)][m]  # noqa: E731

# ================================================================== COVER
p = P("Factibilidad de Proyectos Data Driven · 2C 2026", 10, color=INK2)
P("**Detección anticipada de inventario inmovilizado**", 22, after=2, color=ACCENT)
P("Casa Óga · Retail de Hogar y Decoración", 13, after=2)
P("Entregable 4 · Informe final consolidado (Entregables 1, 2 y 3 con las correcciones aplicadas)", 11, after=12, color=INK2)
T(["Integrante", "Legajo", "Rol en el proyecto", "Entregable clave a cargo"], [
    ["Gianfranco Di Claudio", "64505", "Coordinación", "Plan del proyecto, backlog y sección de cambios"],
    ["Matías Fleischer", "65616", "Datos · calidad y preparación", "Dataset v4 y reglas de limpieza"],
    ["Simón Volpato Escandarani", "64784", "Datos · modelado y evaluación", "Modelo final y ficha del modelo"],
    ["Gerónimo Fasce", "64401", "Visualización", "Tablero de alertas y gráficos"],
    ["Santiago Javier Hernández", "64449", "Comunicación", "Narrativa y presentación final"],
], widths=[4.2, 1.6, 4.4, 6.4])
T(["Versión", "Fecha", "Repositorio con datos, código y evidencias"], [
    ["v4.0 · final", "Noviembre de 2026", "github.com/Gerocasla/Casa-Oga-Data-driven · carpeta «Entregable/Entregable 4»"]],
    widths=[2.4, 3.2, 11.0])

BOX("Sobre este documento", [
    "Integra en una sola pieza lo trabajado en los Entregables 1, 2 y 3 y aplica todas las devoluciones de la cátedra y de "
    "Casa Óga. No repite cada sección de las entregas anteriores: conserva lo necesario para entender y decidir, y remite al "
    "repositorio para el detalle.",
    "**Una cifra, un valor.** Todo el documento usa el corte de agosto de 2026 y el **dataset v4** (reglas de limpieza de Casa Óga, "
    "Entregable 2). El modelo se reentrenó sobre ese dataset y todas las cifras de desempeño y de economía se recalcularon con "
    "`Entregable 4/Modelo/modelo_final_v4.py`. Donde una cifra cambia respecto de lo entregado, la **Sección 12 · Cambios** dice "
    "qué decía, qué dice ahora y por qué.",
    "**Pendiente fuera de nuestro alcance:** las correcciones de maestros de la Ronda 3 (22 costos, 11 duplicados, 4 SKU con dos "
    "proveedores y 6 fechas de apertura) no están incorporadas al dataset. Se declaran como condición previa al piloto, con "
    "responsable y fecha (Secciones 6.4 y 10.3)."])
BREAK()

# ================================================================== EXECUTIVE SUMMARY
H("Resumen ejecutivo")
P(f"**Problema.** Casa Óga detecta tarde el stock que no rota: lo ve en el conteo anual, cuando ya acumuló meses de capital y "
  f"espacio parados. Entre 2023 y 2025 la proporción de posiciones con más de 12 meses de cobertura fue estable (entre 200 y 350 "
  f"posiciones por mes), pero en 2026 se cuadruplicó: **866 posiciones y ARS 178,6 M a costo en agosto de 2026**, con la venta "
  f"de ene-ago 13,4% por debajo de 2025.")
P(f"**Solución.** Una lista mensual por tienda, con revisión humana. Bloque A: la regla «cobertura actual > 12 meses» "
  f"(~{num(fv['bloque_a']['alertas_mes'])} alertas por mes). Bloque B: un modelo de gradient boosting agrega {kb} posiciones por mes "
  f"que todavía no llegan a 12 meses pero van a superarlos dentro de tres. El cupo lo fija el valor de cada alerta, no la capacidad "
  f"de las tiendas: se suman tramos de 50 mientras el tramo acierte más de {pct(vb['precision_equilibrio'])}. La lista se entrega en un "
  f"tablero con una vista por área (3.6).")
P(f"**Desempeño.** A igual cupo, el flujo detecta {pct(fv['flujo']['vp'] / fv['regla_mismo_cupo']['vp'] - 1, 0)} más casos que "
  f"ordenar por cobertura en 2025 ({fv['flujo']['vp']} contra {fv['regla_mismo_cupo']['vp']}) y {pct(ft['flujo']['vp'] / ft['regla_mismo_cupo']['vp'] - 1, 0)} "
  f"más en 2026. 2026 es un año más fácil: la posición sin venta que sigue sin vender pasa de {pct(pers['2025']['proporcion'])} a "
  f"{pct(pers['2026']['proporcion'])}. Por eso el desempeño se informa como rango: recall {pct(fv['flujo']['recall'], 0)} a "
  f"{pct(ft['flujo']['recall'], 0)} y precisión {pct(fv['flujo']['precision'], 0)} a {pct(ft['flujo']['precision'], 0)}.")
P(f"**Factibilidad.** Técnica media (2,25) y legal viable con condiciones (2,2). Económica: en un año como 2025 el proyecto "
  f"recupera la inversión en {num(rv['total']['recupero_meses'])} meses (ROI a 3 años {pct(rv['total']['roi_3anios'])}); la mayor "
  f"parte del valor viene de automatizar la lista con la regla, y el modelo agrega {usd(rv['valor_incremental_modelo_anual'])} por año. "
  f"El resultado es sensible al costo real de desarrollo (con 3 a 4 meses de un científico de datos, ROI a 3 años "
  f"{pct(rv['total_desarrollo_3a4_meses'][0]['roi_3anios'])} a {pct(rv['total_desarrollo_3a4_meses'][1]['roi_3anios'])}) y al valor por "
  f"posición.")
P("**Recomendación.** Avanzar con un piloto supervisado de tres cierres, sin compras nuevas, condicionado a nombrar un responsable "
  "del modelo, estandarizar la exportación mensual, firmar la confidencialidad y reconstruir el dataset con las correcciones de la "
  "Ronda 3. El modelo se mantiene en el bloque B sólo si, con las cohortes maduradas del piloto, supera a la regla a igual cupo.")

H("Resultados clave por sección", 2)
T(["Sección", "Resultado clave"], [
    ["1 · Contexto y problema", "866 posiciones con cobertura > 12 meses (ARS 178,6 M) en ago-26, contra ~200-350 por mes en 2023-2025."],
    ["2 · Objetivos y stakeholders", "Cinco objetivos con mínimo exigible; Sistemas/IT y proveedores externos en el mapa."],
    ["3 · Visión, alcance y plan", "La anticipación la da el modelo. Backlog, plan en 5 fases, metodología CRISP-DM + Scrum y tablero con seis vistas por área."],
    ["4 · Datos", "Dataset v4: 201.310 filas, 60 variables, 3,22% de positivos. 13 hallazgos de calidad con plan. El riesgo está en la cola, no en el promedio."],
    ["5 · Modelo", f"Gradient boosting elegido en validación interna. Flujo regla + modelo: {fv['flujo']['vp']} contra {fv['regla_mismo_cupo']['vp']} casos a igual cupo (2025)."],
    ["6 · Factibilidad técnica", "Media (2,25). Condición crítica: responsable del modelo."],
    ["7 · Factibilidad económica", f"Dos ROI: automatizar la lista (ROI 3 años {pct(rv['automatizacion_sin_modelo']['roi_3anios'])}) e incremental del modelo ({pct(rv['incremental_modelo']['roi_3anios'])}), escenario 2025."],
    ["8 · Factibilidad legal", "Viable con condiciones (2,2): accesos por rol y adenda de confidencialidad."],
    ["9 · Riesgos", "Riesgo crítico 1: que el beneficio no alcance los USD 9.150 anuales que hacen viable el proyecto."],
    ["10 · Solución y go-live", f"Lista de {DB_MES}: {num(DB_N)} alertas, más que la capacidad de las tiendas; se prioriza por capital. Go-live sobre cohortes maduradas."],
    ["11 · Veredicto", "Viable con condiciones como piloto supervisado."],
    ["12 · Cambios", "Qué se modificó respecto de los Entregables 1, 2 y 3, y por qué."],
], widths=[4.6, 12.0])
BREAK()

# ================================================================== 1. CONTEXT
H("1 · Contexto organizacional y problema")
H("1.1 La empresa", 2)
T(["Dimensión", "Descripción"], [
    ["Empresa y sector", "Casa Óga S.A., retail de productos para el hogar y decoración, con más de 10 años de antigüedad."],
    ["Tamaño y geografía", "28 tiendas físicas en cinco regiones (AMBA, Centro, Cuyo, NOA y Patagonia) y un canal de e-commerce."],
    ["Volumen", "$40.254,7 M de venta entre ene-2022 y ago-2026 (reglas v4). Venta 2025: $13.734 M. Precio medio por unidad vendida: $43.353 (el E1 lo llamaba «ticket medio»: no es un ticket, porque los datos no tienen tickets)."],
    ["Catálogo", "800 SKUs históricos, 7 categorías y 25 subcategorías; 634 SKUs activos a dic-25. 250 SKUs explican el 80% de la venta."],
    ["Datos disponibles", "15 fuentes, ene-2022 a ago-2026: Ventas y Stock SKU–tienda–mes (299.400 filas cada una), catálogo, liquidaciones, transferencias, promociones, presupuesto, devoluciones, órdenes de compra, stock de depósito, proveedores, tiendas, calendario, historial de precios y costo de almacenamiento."],
], widths=[3.6, 13.0])

H("1.2 Situación del mercado", 2)
P("El contexto externo empuja a racionalizar el surtido. Las importaciones argentinas crecieron 24,7% en 2025 (USD 75.791 M) y "
  "las de bienes de consumo subieron 17,1% interanual en diciembre de 2025 [1], lo que trae más competencia de precio en productos "
  "importables como bazar y decoración. Al mismo tiempo, la demanda del rubro se enfrió: según CAME, las ventas pyme de bazar, "
  "decoración, textiles de hogar y muebles cayeron 9,7% interanual en noviembre y 15% en diciembre de 2025 [2].")
P("En ese escenario la dirección cambió su prioridad: dejar de expandir el catálogo y racionalizarlo, con foco en rentabilidad y "
  "capital de trabajo. **Corrección respecto del E1:** el índice de estacionalidad 143 (diciembre) contra 61 (enero) era un efecto "
  "del crecimiento del negocio. Ajustada por tendencia, la venta mensual queda entre 98 y 106: no hay estacionalidad relevante "
  "(E2, Parte A §2.3).")

H("1.3 Proceso bajo análisis: gestión de rotación y liquidación de inventario", 2)
P("**Corrección respecto del E1:** el «proceso clave» describía el objetivo del proyecto. El proceso que existe hoy es la "
  "**gestión de rotación y liquidación de inventario**, y funciona así:")
T(["Paso", "Cómo se hace hoy", "Quién"], [
    ["Detección", "Manual y reactiva: percepción en góndola y conteo de inventario de fin de año. No hay definición ni umbral escrito de «stock inmovilizado».", "Responsable comercial de cada categoría"],
    ["Análisis", "Planillas Excel armadas con exportaciones de cada sistema: unas 480 horas por año (360 de tareas mensuales y 120 de cierre).", "Analistas de Comercial y Operaciones"],
    ["Decisión", "Caso por caso, sin protocolo según nivel de riesgo: liquidar, transferir o discontinuar. Descuentos de 10% a 50% fijados por costumbre.", "María G. (liquidar), Lucía O. (transferir), Diego P. y María G. (discontinuar)"],
    ["Ejecución", "Liquidación en tienda o transferencia entre tiendas; demora de 2 a 4 semanas. La devolución al proveedor no está generalizada.", "Responsables de tienda y Operaciones"],
], widths=[2.4, 10.0, 4.2])

H("1.4 Problem statement", 2)
P("Ordenado de afuera hacia adentro: impacto de negocio, síntoma operativo y causa técnica.")
T(["Nivel", "Enunciado"], [
    ["Impacto de negocio", "En ene-ago 2026 la venta cayó 13,4% contra el mismo período de 2025, y las posiciones con más de 12 meses de cobertura pasaron de 200 (dic-25) a **866 en ago-26, con ARS 178,6 M de capital a costo**. Al 5% mensual que informó Casa Óga, mantener ese stock cuesta ARS 8,9 M por mes."],
    ["Por qué no es alarmismo", "Entre 2023 y 2025 el problema estaba estable en proporción: entre 200 y 350 posiciones por mes y una cobertura mediana de 5,2 meses, mientras ventas y stock se duplicaban. El monto en pesos crecía con el negocio. Lo nuevo es 2026: 2 de cada 3 pesos de la caída de venta son los 96 SKUs discontinuados a fin de 2025, y los SKUs que siguen caen 4,8%. Parte del salto puede deberse al nuevo reporte de 2026 (hallazgo H13)."],
    ["Síntoma operativo", "La detección es tardía: el stock se ve en el conteo anual. Las liquidaciones de ene-ago 2026 cayeron 51% justo cuando las posiciones sin venta se multiplicaron por 2,5."],
    ["Causa técnica", "Sistemas en silo sin integración ni BI, consolidación manual en Excel, sin definición formal ni indicador mensual normalizado. Nadie puede distinguir un deterioro real de un efecto de escala, ni anticipar el riesgo."],
    ["Propuesta", "Una lista mensual priorizada por tienda que combine la regla de cobertura con un modelo que anticipa a 3 meses, dimensionada por el valor de cada alerta y con decisión humana."],
], widths=[3.6, 13.0])
IMG(G / "01_posiciones_cobertura12.png", "Figura 1. Posiciones SKU–tienda con stock y más de 12 meses de cobertura (reglas v4). Fuente: E2, Modelo/resultados/insights.json.")
P("**Cifras reconciliadas (corrección prioritaria del E1).** El E1 usaba dos juegos de cifras que no cerraban (661 posiciones y "
  "$83,9 M por un lado; 8,86% → 7,93% y $41,4 M → $93,1 M por otro). Ninguno se pudo reproducir: el script que los calculó no "
  "existe. Desde el E2 el indicador único es la cobertura > 12 meses calculada con un script versionado, y es el que usa todo "
  "este documento.", 9.5)

# ================================================================== 2. OBJECTIVES / STAKEHOLDERS / CONSTRAINTS
H("2 · Objetivos, stakeholders y restricciones")
H("2.1 Objetivo general", 2)
P("Entregar a Casa Óga una lista mensual priorizada de posiciones SKU–tienda en riesgo de superar 12 meses de cobertura dentro de "
  "3 meses, para que Comercial, Compras y Operaciones liquiden, transfieran o frenen compras antes de que el capital quede "
  "inmovilizado, con un volumen de alertas que cada tienda pueda trabajar y que genere más valor del que cuesta revisarlo.")
H("2.2 Objetivos específicos con mínimo exigible", 2)
P("**Corrección del E1:** cada objetivo tiene un mínimo verificable. Los que dependen de algo que todavía no existe se marcan "
  "como no medibles aún.")
T(["Objetivo", "Indicador", "Mínimo exigible", "Estado"], [
    ["OE1 · Target aprobado", "Definición «cobertura > 12 meses en t+3» aprobada por escrito", "Aprobación de María G. con visto bueno de Carlos F.", "Pendiente de firma"],
    ["OE2 · Datos consolidados", "Dataset reproducible con reglas acordadas", "100% de claves sin duplicar y 0 filas con stock negativo en el lote mensual", "Cumplido en v4; Ronda 3 pendiente"],
    ["OE3 · Modelo útil", "Casos detectados a igual cupo contra la regla, validación 2025 y test 2026", "Superar a la regla en los dos períodos", f"Cumplido: {fv['flujo']['vp']} vs {fv['regla_mismo_cupo']['vp']} y {ft['flujo']['vp']} vs {ft['regla_mismo_cupo']['vp']}"],
    ["OE4 · Impacto económico", "Valor neto recuperado por las alertas trabajadas", "Beneficio anual ≥ USD 9.150 (ROI a 3 años ≥ 0)", "No medible aún: requiere registro de acciones del piloto"],
    ["OE5 · Accionable", "Alertas por tienda por mes", "Entre 10 y 25 por tienda; nunca más de 700 en la cadena", f"Cumplido: ~{num(fv['flujo']['alertas_mes'] / 28)} por tienda en 2025"],
], widths=[3.2, 4.4, 4.6, 4.4])

H("2.3 Mapa de stakeholders", 2)
P("**Corrección del E1:** la influencia se separa en dos columnas, porque quien dimensiona la solución no es necesariamente quien "
  "decide; y se suman Sistemas/IT y los proveedores externos, que condicionan la parte técnica.")
T(["Stakeholder", "Rol", "Interés", "Influencia técnica / de diseño", "Influencia de decisión", "Expectativa (fuente)"], [
    ["María G.", "Dirección Comercial · sponsor", "Alto", "Media", "Alta", "Lista accionable y aprobación del target (E1, relevamiento)"],
    ["Carlos F.", "Dirección Financiera · co-decisor", "Alto", "Media", "Alta", "Capital liberado y supuestos de costo validados (E1)"],
    ["Diego P.", "Compras y Categorías", "Medio", "Media", "Media", "Riesgo por SKU y proveedor; autoriza acceso a costos (E1)"],
    ["Lucía O.", "Operaciones · dueña funcional propuesta", "Medio", "Alta", "Baja", "Cupo ejecutable y transferencias (E1, Ronda 2)"],
    ["Responsables de tienda (28)", "Usuarios finales", "Medio", "Alta: su capacidad (15-25/mes) dimensiona la salida", "Baja", "Lista simple, sin sistema nuevo (E1)"],
    ["Sistemas / IT", "Sin responsable: renunció sin dejar documentación", "Medio", "Alta", "Baja", "Supuesto del equipo: exportaciones estables (Ronda 2, P3-P4)"],
    ["Proveedor del POS", "Externo", "Bajo", "Alta: define la exportación y la venta neta", "Media (cotiza)", "Cotización de exportación programada (Ronda 3)"],
    ["Proveedor del sistema de promociones", "Externo", "Bajo", "Media (H10)", "Baja", "Supuesto del equipo"],
    ["Consultora (equipo del proyecto)", "Externo", "Alto", "Alta", "Baja", "Acceso limitado y adenda de confidencialidad (Sección 8)"],
], widths=[2.6, 2.8, 1.4, 3.0, 2.2, 4.6], size=8)

H("2.4 Restricciones, reclasificadas", 2)
P("**Corrección del E1:** cada restricción va en su categoría y sin duplicados. Lo que era un hallazgo de calidad pasa a la "
  "Sección 4, y lo que era una decisión de alcance, a la 3.2.")
T(["Tipo", "Restricción", "Impacto"], [
    ["Tecnológica", "Sin repositorio central ni integración: exportaciones manuales de sistemas en silo. Por eso la granularidad es mensual.", "Pipeline propio en Python; corrida mensual en batch."],
    ["Tecnológica", "Solución liviana y open source elegida por el negocio; inventario sin API.", "Python, GitHub, SharePoint existente; sin cloud en esta etapa."],
    ["Organizacional (capacidad)", "Sin área de datos ni IT interna.", "Hay que nombrar un mantenedor antes del go-live."],
    ["RRHH / disponibilidad", "Poca disponibilidad de responsables de tienda, Compras, Finanzas y Comercial (en el E1 figuraba como temporal).", "Sesiones de validación cortas y planificadas: 30 minutos por cierre."],
    ["Temporal", "Resultados antes del cierre de inventario de fin de año; acción de 2 a 4 semanas.", "Horizonte de predicción de 3 meses; piloto de 3 cierres."],
    ["Presupuestaria", "USD 30.000 de inversión inicial y USD 6.000 por año de referencia.", "Sin licencias nuevas ni consultoría adicional."],
    ["Regulatoria", "Ley 25.326 (no aplica hoy: sin datos personales), 24.766 (confidencialidad) y 11.723 (propiedad del código).", "Accesos por rol y adenda de confidencialidad (Sección 8)."],
], widths=[3.2, 7.6, 5.8])

# ================================================================== 3. VISION / SCOPE / BACKLOG / PLAN
H("3 · Visión, alcance, backlog y plan")
H("3.1 Visión del producto", 2)
T(["Elemento", "Enunciado"], [
    ["PARA", "Dirección Comercial, Compras y Operaciones de Casa Óga,"],
    ["QUE", "necesitan intervenir el stock antes de que quede inmovilizado,"],
    ["EL", "«Dead Stock Anticipator»"],
    ["ES", "una lista mensual priorizada por tienda, con el motivo de cada alerta,"],
    ["QUE", "combina lo que ya está sobrestockeado (regla de cobertura) con lo que **el modelo anticipa a 3 meses**,"],
    ["A DIFERENCIA DE", "el conteo anual y la percepción en góndola,"],
    ["NUESTRO PRODUCTO", "dimensiona la lista por el valor de cada alerta y deja la decisión en las personas."],
], widths=[3.4, 13.2], first_bold=True)
P("**Corrección del E1:** la anticipación la da el modelo (bloque B), entrenado con información hasta el mes t para predecir t+3. "
  "El semáforo del dashboard y la regla (bloque A) muestran el estado presente y no anticipan.")

H("3.2 Alcance", 2)
T(["Dentro del alcance", "Fuera del alcance"], [
    ["Lista mensual de alertas para las 28 tiendas físicas: bloque A (regla) y bloque B (modelo).", "E-commerce: otra plataforma y datos personales (decisión del negocio)."],
    ["Pipeline mensual de limpieza y features con las reglas del E2.", "Liquidación o compra automática: decide una persona."],
    ["Tablero por área (3.6), publicado en SharePoint. **Es un corte mensual que se regenera en cada cierre, no un tablero en vivo.**", "Integración por API (el inventario no la tiene) y cloud."],
    ["Registro de acciones y medición a t+3 del modelo contra la regla.", "Optimización de compras y precio de liquidación."],
], widths=[8.3, 8.3])

H("3.3 Backlog inicial priorizado", 2)
P("**Corrección del E1:** el título prometía un backlog que no existía. El backlog alimenta las fases (3.4) y se refina sprint a "
  "sprint; la prioridad usa MoSCoW (M = imprescindible, S = importante, C = deseable).")
T(["Épica", "Historia de usuario", "Prioridad", "Estado"], [
    ["E1 · Datos", "Como mantenedor, quiero recibir los 5 archivos mensuales con clave fija para correr el lote sin limpieza manual.", "M", "Pendiente (exportación cotizada)"],
    ["E1 · Datos", "Como analista, quiero aplicar las reglas de limpieza H1/H4 en un script para que cada corrida dé lo mismo.", "M", "Hecho (E2)"],
    ["E1 · Datos", "Como Compras, quiero incorporar las correcciones de la Ronda 3 para que el capital y el target usen maestros correctos.", "M", "Pendiente: precondición del piloto"],
    ["E2 · Target", "Como Dirección Comercial, quiero aprobar la definición de riesgo para que la lista tenga un criterio único.", "M", "Pendiente de firma"],
    ["E3 · Modelo", "Como Operaciones, quiero una lista ordenada por riesgo y valor para trabajar primero lo que más rinde.", "M", "Hecho (Sección 5)"],
    ["E3 · Modelo", "Como responsable de tienda, quiero ver el motivo de cada alerta para justificar la acción.", "M", "Hecho (importancia y motivo por fila)"],
    ["E4 · Entrega", "Como responsable de tienda, quiero ver sólo mis alertas y sin costos.", "M", "Pendiente (grupos SharePoint)"],
    ["E4 · Entrega", "Como Finanzas, quiero el capital en riesgo y el valor recuperado por mes.", "S", "Diseñado (tablero)"],
    ["E5 · Seguimiento", "Como sponsor, quiero medir a t+3 si el modelo supera a la regla para decidir si continúa.", "M", "Diseñado (Sección 10)"],
    ["E5 · Seguimiento", "Como mantenedor, quiero una alerta de drift para no publicar alertas en un régimen distinto.", "S", "Diseñado"],
    ["E6 · Evolución", "Como Compras, quiero alertas sobre SKUs nuevos antes de su primer año.", "C", "Fuera de la V1"],
    ["E6 · Evolución", "Como Dirección, quiero sumar e-commerce.", "C", "Fuera de la V1"],
], widths=[2.6, 9.4, 1.6, 3.0], size=8.5)

H("3.4 Plan del proyecto", 2)
T(["Fase", "Duración", "Responsable", "Criterio de cierre"], [
    ["0 · Entendimiento de negocio y datos", "Hecha (ago-sep 2026)", "Di Claudio", "Relevamiento, EDA y dashboard descriptivo (E1)"],
    ["1 · Calidad y preparación", "Hecha (sep-oct 2026)", "Fleischer", "Dataset v4 con reglas de Casa Óga (E2)"],
    ["2 · Modelado y factibilidad", "Hecha (oct-nov 2026)", "Volpato", "Modelo final en validación y test; veredicto integrado (E3 y E4)"],
    ["3 · Preparación del piloto", "4 semanas", "Di Claudio con Sistemas", "Los 5 criterios de go-live de 10.3 cumplidos"],
    ["4 · Piloto supervisado", "3 cierres + 3 meses de maduración", "Lucía O. y el mantenedor", "Tres cohortes maduradas medidas contra la regla"],
], widths=[4.6, 3.8, 3.6, 4.6])
T(["Hito", "Fecha objetivo", "Responsable", "Evidencia"], [
    ["Target aprobado y Ronda 3 incorporada", "Semana 2 de la fase 3", "María G. · Fleischer", "Acta firmada; dataset v5 y comparación v4 → v5"],
    ["Mantenedor nombrado y adenda firmada", "Semana 3", "Dirección", "Designación y adenda"],
    ["Primera corrida real publicada", "Cierre 1 (C1)", "Mantenedor", "Control de recepción y lista publicada"],
    ["Decisión de continuidad", "Mes 6 (tres cohortes maduradas)", "Carlos F.", "Informe de piloto (Sección 10.2)"],
], widths=[5.0, 3.6, 3.6, 4.4])
T(["Precondición", "Responsable", "Plazo", "Consecuencia si no se cumple"], [
    ["Nombrar mantenedor (5-6 h por semana)", "María G.", "Antes de C1", "No se publica el lote; el modelo se degrada sin control."],
    ["Exportación mensual estandarizada", "Sistemas y Lucía O.", "Antes de C1", "Limpieza manual en cada corrida; se repite el fracaso de la consultora anterior."],
    ["Reconstruir el dataset con la Ronda 3 y reevaluar", "Fleischer (Compras entrega los archivos)", "Semana 2 de la fase 3", "Las métricas siguen calculadas sobre maestros que Casa Óga ya corrigió."],
    ["Adenda de confidencialidad y accesos por rol", "Dirección y Sistemas", "Antes del primer acceso a datos reales", "Exposición de costos y condiciones de proveedores."],
], widths=[4.8, 3.6, 3.2, 5.0])

H("3.5 Metodología", 2)
P("Se mantiene el enfoque del E1: **CRISP-DM para el ciclo de datos y Scrum para gestionar el trabajo**. Lo que agrega este "
  "documento es cómo se aplicó: cada fase de CRISP-DM quedó en un entregable, y las respuestas de Casa Óga obligaron a volver "
  "atrás varias veces, que es lo que el enfoque prevé.")
T(["Fase CRISP-DM", "Dónde quedó", "Iteraciones que hubo"], [
    ["Entendimiento del negocio", "E1: relevamiento, objetivos, stakeholders y definición de dead stock propuesta por el equipo", "Rondas 1 y 2 de preguntas; la definición de riesgo pasó de «sin venta en 3 meses» (azar en el 22% de los casos de bajo volumen) a cobertura > 12 meses"],
    ["Entendimiento de los datos", "E1 y E2: perfil de las 15 fuentes, 13 hallazgos de calidad (4.2) y analítica descriptiva (4.4)", "Al llegar los datos de 2026 se rehízo el EDA al corte ago-26"],
    ["Preparación", "E2: reglas de limpieza y dataset de entrenamiento (4.3)", "Cuatro versiones del dataset (v1 a v4), cada una por una respuesta de Casa Óga o una devolución de la cátedra"],
    ["Modelado y evaluación", "E3 y este informe (5)", "Modelo reentrenado sobre la v4; selección movida a la validación interna 2024"],
    ["Despliegue", "Diseño de la solución, tablero y piloto (3.6, 10)", "Pendiente: piloto supervisado de tres cierres"],
], widths=[3.4, 6.4, 6.8], size=8.5)
T(["Elemento", "Decisión", "Por qué"], [
    ["Gestión", "Scrum con sprints de 2 semanas y el backlog de 3.3, refinado en cada sprint", "Comercial y Finanzas tienen poca disponibilidad y necesitan ver avances parciales"],
    ["Validación con el negocio", "Una ronda de preguntas por etapa (Rondas 1 a 3) y reglas de limpieza firmadas por Casa Óga", "Un intento anterior con una consultora fracasó por no poder consolidar los datos"],
    ["Herramientas", "Git y GitHub; Python (pandas, scikit-learn, LightGBM); planilla para validar; HTML para los tableros", "Equipo reducido y sin área de datos en Casa Óga: stack liviano, documentado y sin licencias"],
    ["Reproducibilidad", "Cada cifra sale de un script del repositorio (Anexo)", "Que la cátedra y el futuro mantenedor obtengan los mismos números"],
], widths=[3.0, 7.0, 6.6], size=8.5)

H("3.6 Tablero de seguimiento por área", 2)
P("**Corrección del E1:** el tablero del E1 era descriptivo y cortaba en dic-25. El tablero final (`Entregable 4/Casa-Oga-Dashboard.html`) "
  f"muestra la lista que generó el modelo para {DB_MES}, con datos hasta ese mes, y una vista por área. Es un único archivo HTML que funciona sin "
  "conexión. Tiene filtros por región, tienda, categoría, proveedor, origen de la alerta, acción y cupo, y se descarga en CSV. En cada "
  "cierre se regenera con dos scripts: uno puntúa el mes y el otro arma el archivo.")
T(["Vista", "Usuario", "Pregunta que responde", "Indicadores"], [
    ["Resumen", "Dirección Comercial y Financiera (María G., Carlos F.)", "¿Cuánto capital está en riesgo y la solución funciona?", "Alertas del mes, capital en alerta, alertas dentro del cupo, casos extra contra la regla, ROI"],
    ["Tiendas", "Operaciones (Lucía O.) y responsables de tienda", "¿Qué hago este mes en mi tienda?", "Lista ordenada por capital, cupo de 25, acción sugerida con destino y tres señales por alerta"],
    ["Lista de alertas", "Todas las áreas", "¿Qué posiciones cumplen un criterio?", "Tabla completa con búsqueda, orden y descarga"],
    ["Compras y categorías", "Compras (Diego P.)", "¿Qué no volver a comprar?", "Capital por categoría y proveedor; SKUs en alerta en más de una tienda"],
    ["Economía", "Finanzas (Carlos F.)", "¿Se paga?", "Dos ROI, valor neto según la cantidad de alertas, sensibilidad"],
    ["Modelo", "Mantenedor y equipo de datos", "¿El modelo sigue funcionando?", "Recall según el cupo, precisión por tanda, importancia de variables, recall por segmento con IC 95%"],
], widths=[2.4, 3.6, 4.0, 6.6], size=8.5)
P("La acción es una sugerencia y la decide la tienda con Comercial y Compras. El orden de las reglas es este:")
B(["**Transferir** si el SKU no sobra en la cadena (cobertura de cadena < 12) y otra tienda lo vende a 1 unidad o más por mes con menos de 3 meses de cobertura.",
   "**Frenar compra** si hay órdenes pendientes del SKU.",
   "**Frenar reposición** si la alerta es del modelo y la posición todavía vende.",
   "**Liquidar** en los demás casos."])
P("Las señales son los tres datos de la posición que más se apartan del resto de la cadena. Ayudan a entender la alerta, pero no "
  "son una relación causal. La versión entregada muestra costos porque es para la cátedra y la Dirección. La de tiendas se publica "
  "sin la columna de capital (8).", 9.5)

# ================================================================== 4. DATA
H("4 · Datos: calidad y preparación")
H("4.1 Inventario de fuentes", 2)
P("**Corrección del E3:** el Calendario llega hasta agosto de 2026 (1.704 filas) y los costos de los 22 SKUs ya los envió Casa "
  "Óga: no figuran como pedidos pendientes. El factor ×1,2321 se conserva sólo en el dataset v4, hasta incorporar esos costos.")
T(["Fuente", "Período", "Registros", "Calidad", "Rol", "Usada en la V1"], [
    ["Ventas SKU–tienda–mes", "ene-22 a ago-26", "299.400", "Media (H1, H4, H13)", "Crítica: target y demanda", "Sí"],
    ["Stock SKU–tienda–mes", "ene-22 a ago-26", "299.400", "Media (H4, H5, H6)", "Crítica: target", "Sí"],
    ["Catálogo de productos", "altas hasta jun-25", "815 (800 SKUs)", "Media (H2, H11)", "Crítica: universo y atributos", "Sí"],
    ["Órdenes de compra · Transferencias · Liquidaciones · Promociones", "ene-22 a ago-26", "3.000 · 4.200 · 593 · 119", "Buena a media (H7, H10)", "Útil", "Sí (variables)"],
    ["Stock depósito · Proveedores · Tiendas · Presupuesto", "ene-22 a ago-26", "23.858 · 10 · 28 · 10.976", "Media (H3, H9)", "Útil", "Sí (variables)"],
    ["Calendario", "hasta ago-26", "1.704", "Buena", "Opcional", "No"],
    ["Devoluciones · Historial de precios · Costo almacenamiento", "hasta dic-25 / reconstrucción / constante", "2.317 · 1.498 · 7", "Baja (H8, H12)", "Opcional", "No"],
], widths=[4.0, 2.6, 2.6, 2.6, 2.8, 2.0], size=8)

H("4.2 Hallazgos de calidad y plan de mejora", 2)
P("Trece hallazgos, todos con tratamiento en el proyecto y acción en origen (detalle en el E2, Parte B §1.1 y §1.2).")
T(["Id", "Hallazgo", "Tratamiento en el proyecto", "Acción en origen · responsable · plazo"], [
    ["H1-H2", "2.378 claves duplicadas en Ventas y Stock por 15 SKUs cargados dos veces", "Conservar el registro con venta real o de mayor venta (regla de Casa Óga)", "Clave única del maestro · Compras y Sistemas · 1 mes"],
    ["H3", "6 tiendas con ventas antes de su apertura ($1.471,7 M)", "Antigüedad de tienda excluida del modelo", "Auditar fechas · Operaciones · 1 mes (Ronda 3: 6 fechas corregidas, a incorporar)"],
    ["H4-H5", "Ventas negativas (devoluciones) y stock negativo o menor a la venta", "Stock negativo a 0; devoluciones neteadas salvo «sin rotación»", "Sincronizar POS-inventario · Sistemas · 3 meses"],
    ["H6", "Stock en tránsito sin conciliar (9 veces las transferencias)", "Variable excluida", "Definir el campo · Operaciones · 1 mes"],
    ["H7", "Liquidaciones «Discontinuación» sobre SKUs activos; «Todas» es válido (28 tiendas)", "Se usan como acción pasada, sin motivo", "Validación de motivo · Comercial · 1 mes"],
    ["H8-H9-H10", "Historial de precios reconstruido; descuentos fuera de rango; promociones duplicadas", "Excluidos o no usados", "Validaciones de carga · Comercial y proveedor · 1-3 meses"],
    ["H11", "22 SKUs sin costo", "Costo de OC × 1,2321 (supuesto, sólo v4)", "No activar sin costo · Compras · inmediato (Ronda 3: costos entregados)"],
    ["H12", "Devoluciones y catálogo no cubren 2026", "Declarado como limitación", "Extender a ago-26 · referente de datos · 1 mes"],
    ["H13", "2026 viene de otro reporte con reglas no documentadas: H1, H4 y H5 no se dan por resueltos", "Validación 2025 y test 2026 reportados por separado", "Documentar reglas y mantener un extracto sin consolidar · Operaciones y Sistemas · 1 mes"],
], widths=[1.6, 5.0, 4.6, 5.4], size=8)

H("4.3 Dataset de entrenamiento v4", 2)
T(["Elemento", "Definición"], [
    ["Pregunta", "¿Qué posiciones SKU–tienda activas van a superar 12 meses de cobertura dentro de 3 meses?"],
    ["Unidad y universo", "SKU–tienda–mes con stock > 0 en t, no discontinuada, 3+ meses de historia y t+3 observado."],
    ["Target", "1 si cobertura en t+3 > 12 meses (stock / promedio de 12 meses de unidades netas)."],
    ["Tamaño", "201.310 filas × 60 variables (55 numéricas y 5 categóricas); 6.490 positivos (3,22%); peso de clase 42,1."],
    ["Partición temporal con embargo de 3 meses", "Train mar-22 a dic-24 (98.653 filas, 2,32%) · validación abr-sep 25 (38.360, 2,08%) · test ene-may 26 (28.070, 8,84%)."],
    ["Exclusión por t+3", "70.416 filas (25,9%), con el mismo perfil que el universo por categoría, tienda y stock (E2 §2.1)."],
    ["Sensibilidad a las reglas de Casa Óga", "Deduplicar por mayor venta: −34 positivos. Sacar «sin rotación» del neteo: −330. Prevalencia v3 → v4: 3,40% → 3,22%; peso de clase 39,0 → 42,1."],
    ["Leakage", "Toda variable se calcula con información ≤ t. Excluidos: precio y costo del catálogo (son el valor de hoy), stock en tránsito, presupuesto revisado y acciones posteriores a t."],
], widths=[4.2, 12.4])

H("4.4 Analítica descriptiva: qué muestran los datos", 2)
P("Los hallazgos del E2 (Parte A §2.3 y Anexo A) que definen el diseño de la solución. El detalle y los gráficos están en el E2 y en "
  "su tablero descriptivo, en el repositorio.")
T(["Pregunta", "Hallazgo", "Qué implica para el proyecto"], [
    ["¿La venta crece porque los productos rotan más?", "No. Las posiciones con venta pasan de 17 (ene-22) a más de 8.000 (dic-25), mientras las unidades por posición se mantienen en ~3,2 por mes.", "El crecimiento viene de abrir tiendas y sumar productos. El stock crece con la red, no por mejor rotación."],
    ["¿Por qué cae 2026?", "Dos tercios de la caída vienen de los 96 SKUs discontinuados a fin de 2025; no hay altas desde jul-25. Los SKUs activos caen 4,8% y casi recuperan en agosto.", "Es una caída de surtido, no de demanda. Los datos de 2026 vienen de otro reporte (H13)."],
    ["¿Dónde está el riesgo?", "La mediana de cobertura se mantiene en ~5 meses, pero en 2026 el percentil 90 pasa de 9 a 12 meses y el 99 de 16 a 48. Las posiciones sin venta en 3 meses pasan de 365 (dic-25) a 929 (ene-mar 26), mientras las liquidaciones caen 51%.", "El riesgo está en pocas posiciones y no en el promedio. Por eso la solución trabaja posición por posición y no con indicadores agregados."],
    ["¿Hay estacionalidad?", "Ajustado por tendencia, el índice mensual va de 98 a 106. No se ve efecto diferenciado de Hot Sale, Black Friday ni Navidad.", "No hace falta un modelo estacional. Los eventos entran como una sola variable de calendario."],
    ["¿Qué tan concentrada está la venta?", "250 de 798 SKUs (31%) explican el 80% de la venta.", "La cola larga de baja contribución es el universo natural del riesgo."],
    ["¿Difieren las tiendas?", "Cada tienda tiene entre 3,0% y 4,1% de la venta. La correlación entre venta y m² es −0,21. Las regiones venden en proporción a la cantidad de tiendas.", "Un cupo igual por tienda (15 a 25 alertas) es razonable como punto de partida."],
    ["¿Sirven el presupuesto y el lead time?", "El presupuesto se cumple al ~90% en todos los niveles y años. El lead time real coincide con el declarado (+1 día en promedio).", "El presupuesto no es una meta independiente: entra sólo como cumplimiento de 3 meses. El lead time entra como variable."],
], widths=[3.4, 7.2, 6.0], size=8.5)
P("El efecto de las reglas de limpieza se ve en el tablero de calidad antes y después del E2 (§1.3): 11 métricas, con los cambios "
  "más grandes en las posiciones duplicadas y en la venta neta de devoluciones.", 9.5)

# ================================================================== 5. MODEL
H("5 · Modelo: experimento, selección y evaluación")
H("5.1 Una sola métrica para todas las etapas", 2)
P(f"**Corrección del E3:** la métrica principal cambiaba tres veces (PR-AUC, recall con umbral 0,5 y Recall@600). Desde ahora "
  f"todo se compara con la misma: **casos detectados (recall) y valor neto en el cupo mensual de alertas**, con la PR-AUC como "
  f"métrica secundaria. El valor neto usa los valores unitarios de la Parte B del E3 con el capital por posición reproducible del "
  f"E2: un acierto vale {usd(vb['valor_vp_usd'])} y una alerta falsa cuesta {usd(vb['costo_fp_usd'])}, ambos con 70% de adopción. "
  f"Una alerta paga si el tramo acierta más del **{pct(vb['precision_equilibrio'])}**.")

H("5.2 Candidatos y línea base en los tres períodos", 2)
P(f"La línea base es la regla que Casa Óga puede calcular hoy en Excel: «cobertura actual > 12 meses» "
  f"(~{num(pv['regla_fija']['alertas_mes'])} alertas por mes en 2025) y, para comparar a igual cupo, la cobertura usada como "
  f"ranking. **Corrección del E3:** la tabla incluye también el período de entrenamiento.")
rows = []
for per, lbl in (("train", "Train (34 meses)"), ("validacion", "Validación 2025"), ("test", "Test 2026")):
    P_ = R["periodos"][per]
    for m, ml in (("Regla", "Regla (cobertura)"), ("Logistica", "Regresión logística"), ("HistGradientBoosting", "Gradient boosting"), ("Ensamble", "Ensamble de 3 árboles")):
        rows.append([lbl if m == "Regla" else "", ml, f"{c(per, 175, m)['vp']} ({pct(c(per, 175, m)['recall'], 0)})",
                     f"{c(per, 300, m)['vp']} ({pct(c(per, 300, m)['recall'], 0)})", f"{c(per, 600, m)['vp']} ({pct(c(per, 600, m)['recall'], 0)})",
                     num(P_['pr_auc'][m], 3)])
T(["Período", "Modelo", "Top-175 VP (recall)", "Top-300", "Top-600", "PR-AUC"], rows, widths=[2.8, 3.6, 2.8, 2.4, 2.4, 1.6], size=8.5)
P(f"Positivos: train {num(ptr['positivos'])}, validación {pv['positivos']} y test {num(pt_['positivos'])}. El ensamble llega a "
  f"una PR-AUC de {num(ptr['pr_auc']['Ensamble'], 2)} en entrenamiento contra {num(pv['pr_auc']['Ensamble'], 2)} en validación: es el "
  f"que más sobreajusta.", 9.5)

H("5.3 Selección del modelo: gradient boosting solo", 2)
v = lambda k, m: vi[f"top_{k}"][m]["vp"]  # noqa: E731
P(f"**Corrección del E3:** el ensamble se había elegido comparando combinaciones en la validación 2025, que así dejaba de ser "
  f"independiente. Ahora la selección se hace en una **validación interna** (entrenamiento hasta mar-24, embargo abr-jun 24, "
  f"evaluación jul-dic 24, {vi['positivos']} positivos), con una regla fijada antes de mirar: el ensamble sólo se adopta si supera "
  f"al gradient boosting en los cupos de 175, 300 y 420. No lo hace (Top-175: {v(175, 'Ensamble')} contra {v(175, 'HistGradientBoosting')}; "
  f"Top-300: {v(300, 'Ensamble')} contra {v(300, 'HistGradientBoosting')}; Top-420: {v(420, 'Ensamble')} contra {v(420, 'HistGradientBoosting')}). "
  f"Se elige el **gradient boosting**: un solo modelo, menos sobreajuste y más fácil de explicar y mantener. La regresión logística "
  f"queda cerca, a {v(300, 'HistGradientBoosting') - v(300, 'Logistica')} casos en Top-300, y sigue siendo la alternativa si el mantenedor "
  f"necesita algo más simple.")

H("5.4 Punto de operación: el cupo lo fija el valor, no la capacidad", 2)
tr = R["punto_operacion"]["tramos_bloque_b_validacion"]
P(f"**Corrección del E3:** las 600 alertas por mes llenaban la capacidad aunque las últimas costaran más de lo que recuperaban. "
  f"La capacidad declarada (420 a 700) es un techo, no una meta. La regla de corte: el bloque A (regla) entra completo y el "
  f"modelo suma tramos de 50 posiciones mientras el tramo acierte más de {pct(vb['precision_equilibrio'])} en la validación 2025. "
  f"Los tramos aciertan {', '.join(pct(t['precision_tramo'], 0) for t in tr[:5])}…: el cuarto tramo ya no paga, de modo que el "
  f"bloque B queda en **{kb} alertas por mes**. El cupo total es de ~{num(fv['flujo']['alertas_mes'])} alertas en 2025 "
  f"(~{num(fv['flujo']['alertas_mes'] / 28)} por tienda) y ~{num(ft['flujo']['alertas_mes'])} en 2026.")
IMG(G / "02_valor_vs_alertas_2025.png", "Figura 2. Valor neto mensual según el número de alertas, validación abr-sep 2025. Fuente: modelo_final_v4_resultados.json.")

H("5.5 Resultado del flujo propuesto en 2025 y 2026", 2)
T(["Componente", "Alertas/mes 2025 → 2026", "Precisión", "Recall", "Casos (VP)", "Valor neto USD/mes"], [
    ["Bloque A · regla", f"{num(fv['bloque_a']['alertas_mes'])} → {num(ft['bloque_a']['alertas_mes'])}", f"{pct(fv['bloque_a']['precision'])} → {pct(ft['bloque_a']['precision'])}", f"{pct(fv['bloque_a']['recall'])} → {pct(ft['bloque_a']['recall'])}", f"{fv['bloque_a']['vp']} / {num(ft['bloque_a']['vp'])}", f"{num(fv['bloque_a']['valor_neto_mes_usd'])} → {num(ft['bloque_a']['valor_neto_mes_usd'])}"],
    ["Bloque B · modelo", f"{kb} → {kb}", f"{pct(fv['bloque_b']['precision'])} → {pct(ft['bloque_b']['precision'])}", f"{pct(fv['bloque_b']['recall'])} → {pct(ft['bloque_b']['recall'])}", f"{fv['bloque_b']['vp']} / {ft['bloque_b']['vp']}", f"{num(fv['bloque_b']['valor_neto_mes_usd'])} → {num(ft['bloque_b']['valor_neto_mes_usd'])}"],
    ["**Flujo A + B**", f"{num(fv['flujo']['alertas_mes'])} → {num(ft['flujo']['alertas_mes'])}", f"{pct(fv['flujo']['precision'])} → {pct(ft['flujo']['precision'])}", f"{pct(fv['flujo']['recall'])} → {pct(ft['flujo']['recall'])}", f"{fv['flujo']['vp']} / {num(ft['flujo']['vp'])}", f"{num(fv['flujo']['valor_neto_mes_usd'])} → {num(ft['flujo']['valor_neto_mes_usd'])}"],
    ["Cobertura, mismo cupo", "igual", f"{pct(fv['regla_mismo_cupo']['precision'])} → {pct(ft['regla_mismo_cupo']['precision'])}", f"{pct(fv['regla_mismo_cupo']['recall'])} → {pct(ft['regla_mismo_cupo']['recall'])}", f"{fv['regla_mismo_cupo']['vp']} / {num(ft['regla_mismo_cupo']['vp'])}", f"{num(fv['regla_mismo_cupo']['valor_neto_mes_usd'])} → {num(ft['regla_mismo_cupo']['valor_neto_mes_usd'])}"],
    ["Referencia: modelo Top-600", "600 → 600", f"{pct(fv['modelo_top600']['precision'])} → {pct(ft['modelo_top600']['precision'])}", f"{pct(fv['modelo_top600']['recall'])} → {pct(ft['modelo_top600']['recall'])}", f"{fv['modelo_top600']['vp']} / {num(ft['modelo_top600']['vp'])}", f"{num(fv['modelo_top600']['valor_neto_mes_usd'])} → {num(ft['modelo_top600']['valor_neto_mes_usd'])}"],
], widths=[3.4, 2.8, 2.8, 2.6, 2.4, 2.6], size=8.5)
IMG(G / "03_flujo_vs_regla.png", "Figura 3. Casos detectados en cada período con el mismo número de alertas. Fuente: modelo_final_v4_resultados.json.")
P(f"**Lectura.** En 2025 el modelo agrega {fv['flujo']['vp'] - fv['regla_mismo_cupo']['vp']} casos sobre la regla a igual cupo "
  f"(+{pct(fv['flujo']['vp'] / fv['regla_mismo_cupo']['vp'] - 1, 0)}); en 2026, sólo {ft['flujo']['vp'] - ft['regla_mismo_cupo']['vp']} "
  f"(+{pct(ft['flujo']['vp'] / ft['regla_mismo_cupo']['vp'] - 1, 0)}). El modelo le gana a la regla en los dos bloques, así que es "
  f"robusto; pero su ventaja es chica justo en el año fácil. **Por qué 2026 es más fácil** (pedido de la cátedra, verificado con "
  f"nuestros datos): de las posiciones con stock y sin venta en un mes de ene-may, siguen sin vender los tres meses siguientes "
  f"{pct(pers['2025']['proporcion'])} en 2025 ({num(pers['2025']['siguen_sin_vender'])} de {num(pers['2025']['posiciones_mes'])}) y "
  f"{pct(pers['2026']['proporcion'])} en 2026 ({num(pers['2026']['siguen_sin_vender'])} de {num(pers['2026']['posiciones_mes'])}). Con "
  f"esa persistencia la cobertura sola casi separa los casos (AUC {num(pt_['auc']['Regla'], 2)}). Por eso el desempeño esperado "
  f"es un rango y no el número de 2026.")
P(f"**Cupo en un régimen como 2026.** Con precisiones de 65% en el bloque B, más alertas sí pagan: a 600 por mes el valor sería "
  f"{usd(ft['flujo_600']['valor_neto_mes_usd'])} contra {usd(ft['flujo']['valor_neto_mes_usd'])} por mes. Por eso el cupo no es fijo: "
  f"en el piloto se agrega o se quita un tramo de 50 según la precisión madurada del último tramo (Sección 10.2).", 9.5)

H("5.6 Explicabilidad y errores por segmento", 2)
P(f"**Corrección del E3:** la importancia se mide sobre el sistema completo y en la métrica del negocio. Se mezcla al azar cada "
  f"variable y se mide cuántos casos pierde el Top-{imp['k']} mensual en la validación 2025 (base: {imp['vp_base']} casos). Las tres "
  f"variables que pesan son la venta de 6 meses, la cobertura actual y la variabilidad de la venta: el modelo mira lo mismo que "
  f"un comprador, pero lo combina antes de que la cobertura cruce los 12 meses. Cada alerta lleva su motivo en lenguaje de tienda "
  f"(por ejemplo: «sin ventas en 6 meses y 4 unidades en stock»).")
IMG(G / "04_importancia_permutacion.png", "Figura 4. Importancia por permutación del modelo final. Fuente: modelo_final_v4_resultados.json.")
rows = []
for key, lbl in (("validacion", "2025"), ("test", "2026")):
    for grp in ("region", "categoria"):
        for z in seg[key][grp]:
            if z["segmento"] in ("Patagonia", "Cuyo", "Cocina y mesa", "Muebles"):
                rows.append([lbl, z["segmento"], f"{z['vp']} de {z['positivos']}", pct(z["recall"]),
                             f"{pct(z['ic95'][0], 0)} a {pct(z['ic95'][1], 0)}", pct(seg[key]["recall_global"]),
                             "Sí" if z["global_dentro_ic"] else "No"])
T(["Año", "Segmento", "Detectados", "Recall", "IC 95% (Wilson)", "Recall global", "¿Global dentro del IC?"], rows,
  widths=[1.4, 2.8, 2.4, 1.8, 3.0, 2.4, 2.8], size=8.5)
P(f"**Corrección del E3:** con 18 positivos, el recall de Patagonia en 2025 tiene un intervalo de 20% a 61% que incluye el "
  f"global: no se puede afirmar que el modelo funcione peor allí. Cocina y mesa sí queda debajo del global en 2026 con muestra "
  f"suficiente, y por eso tiene umbral de monitoreo propio (Sección 10.2).", 9.5)

H("5.7 Ficha del modelo", 2)
T(["Campo", "Contenido"], [
    ["Modelo", "HistGradientBoostingClassifier (scikit-learn 1.8): 300 iteraciones, tasa 0,05, pesos de clase balanceados, categóricas nativas."],
    ["Datos", "dataset_entrenamiento_v4: train mar-22 a dic-24; 60 variables calculadas al cierre de t."],
    ["Salida", "Probabilidad no calibrada, usada sólo para ordenar dentro de cada mes. No es una orden de liquidar."],
    ["Uso", f"Bloque B: hasta {kb} posiciones por mes que no están en la regla; decisión humana."],
    ["Desempeño esperado (rango)", f"Recall del flujo {pct(fv['flujo']['recall'], 0)} a {pct(ft['flujo']['recall'], 0)}; precisión {pct(fv['flujo']['precision'], 0)} a {pct(ft['flujo']['precision'], 0)}; valor neto USD {num(fv['flujo']['valor_neto_mes_usd'])} a {num(ft['flujo']['valor_neto_mes_usd'])} por mes."],
    ["Limitaciones", "Datos de 2026 de otro reporte (H13); maestros sin la Ronda 3; no cubre SKUs nuevos ni e-commerce; la ventaja sobre la regla es chica cuando el régimen es persistente."],
    ["Reentrenamiento", "Trimestral, o antes si dispara el monitoreo de 10.2."],
    ["Reproducción", "python \"Entregable/Entregable 4/Modelo/modelo_final_v4.py\" → resultados/modelo_final_v4_resultados.json y log."],
], widths=[3.6, 13.0])

# ================================================================== 6. TECHNICAL FEASIBILITY
H("6 · Factibilidad técnica")
T(["Condición", "Score", "Evidencia"], [
    ["Datos suficientes", "3", "51 meses, 6.490 positivos (2.289 en train); granularidad SKU–tienda–mes igual a la unidad de decisión; claves del target con 100% de match."],
    ["Calidad utilizable", "2", "0% de nulos en el target, pero 13 hallazgos y tres estructurales (precio y costo sin historia, historial reconstruido, stock en tránsito) que obligan a excluir variables. Ronda 3 sin incorporar."],
    ["Infraestructura", "2", "Stack open source suficiente; integración manual. La PC i5/16 GB de oficina existe (confirmada por Casa Óga en la Ronda 3) y es el entorno del piloto: no se compra equipo."],
    ["Capacidad humana", "2", "El equipo construye el modelo; Casa Óga no tiene área de datos ni un mantenedor nombrado."],
    ["**Promedio**", "**2,25**", "**Factibilidad media.** La condición que más pesa es la capacidad humana. Umbral que cambiaría el score: si antes del piloto no se nombra mantenedor, Capacidad humana baja a 1 (promedio 2,0, factibilidad baja)."],
], widths=[3.4, 1.4, 11.8])
H("6.1 Stack", 2)
T(["Capa", "Piloto (MVP)", "Producción", "Costo"], [
    ["Almacenamiento", "CSV y Parquet en SharePoint; código en GitHub", "Igual; base de datos sólo si se automatiza la extracción", "USD 0 (licencias existentes)"],
    ["ETL y modelo", "Python: pandas, scikit-learn (scripts del E2 y del E4)", "Igual, con versiones fijadas", "USD 0"],
    ["Ejecución", "PC de oficina existente, corrida mensual manual con checklist", "Programador de tareas de Windows", "USD 0"],
    ["Entrega", "Planilla y tablero por rol en SharePoint / Microsoft 365", "Igual", "USD 0"],
    ["Exportaciones", "Manual de inventario; programada del POS", "Programadas", "USD 3.000 alta + USD 2.040/año (cotizado)"],
], widths=[3.0, 5.2, 4.8, 3.6])

# ================================================================== 7. ECONOMIC FEASIBILITY
H("7 · Factibilidad económica")
H("7.1 Costos", 2)
T(["Concepto", "Inversión inicial (USD)", "Anual (USD)", "Tipo"], [
    ["Desarrollo del modelo (equipo consultor)", "3.000", "—", "Fijado por el equipo; ver sensibilidad"],
    ["Preparación e integración de datos · limpieza", "1.000 · 800", "—", "Fijado por el equipo"],
    ["Capacitación de 35 usuarios", "900", "—", "Estimación"],
    ["Altas de exportación del POS e inventario", "3.000", "—", "Cotización de Casa Óga, sin IVA"],
    ["Contingencia (10%)", "870", "—", "Sobre la inversión"],
    ["Abonos de exportación", "—", "2.040", "Cotizado: costo de caja"],
    ["Mantenedor interno (5 h por semana × USD 12)", "—", "3.120", "**Costo de oportunidad:** tiempo de personal existente, no es caja"],
    ["Apoyo externo trimestral (reentrenamiento)", "—", "800", "Estimación: costo de caja"],
    ["**Total**", "**9.570**", "**5.960** (2.840 de caja)", ""],
], widths=[6.6, 3.2, 3.0, 3.8])

H("7.2 Beneficios: valor por posición reproducible", 2)
P(f"**Corrección del E3:** el valor por posición salía de cifras del E1 que no se pueden reproducir (ARS 83,9 M / 661 = ARS "
  f"126.929). Ahora se usa la cifra reproducible del E2: **ARS 184,1 M / 882 = ARS {num(vb['capital_por_posicion_ars'])} por posición** "
  f"(USD {num(vb['capital_por_posicion_usd'], 2)} a ARS 1.560). Con las reglas v4 (ARS 178,6 M / 866) es ARS 206.236, 1,2% menos, y no "
  f"cambia ninguna conclusión. La cifra del E1 queda como sensibilidad. Con los mismos supuestos de la Parte B (5% mensual, 3 meses "
  f"ahorrados, liquidación temprana contra tardía, 60% de acciones exitosas y 70% de adopción), un acierto vale "
  f"{usd(vb['valor_vp_usd'])} y una alerta falsa cuesta {usd(vb['costo_fp_usd'])}.")
P("El beneficio tiene tres partes, que ahora se muestran por separado: (1) **horas evitadas** al automatizar el armado de la lista: "
  f"480 h × USD 12 × 70% = {usd(rv['horas_anual'])} por año; (2) **valor neto de la regla** automatizada (bloque A), que no necesita "
  f"modelo; (3) **valor incremental del modelo** (bloque B). La economía se evalúa contra «no hacer nada» y, para el modelo, contra "
  f"la regla de la línea base, como pide la consigna.")

H("7.3 Dos ROI: automatizar la lista y el incremental del modelo", 2)


def rrow(lbl, q):
    return [lbl, usd(q["beneficio_anual"]), usd(q["inversion"]), usd(q["recurrente"]), pct(q["roi_anio1"]), pct(q["roi_3anios"]),
            f"{num(q['recupero_meses'])} meses" if q["recupero_meses"] else "No recupera"]


T(["Escenario 2025 (validación)", "Beneficio anual", "Inversión", "Recurrente", "ROI año 1", "ROI 3 años", "Recupero"], [
    rrow("A · Automatizar la lista con la regla (sin modelo)", rv["automatizacion_sin_modelo"]),
    rrow("B · Incremental del modelo", rv["incremental_modelo"]),
    rrow("**Total del flujo propuesto (A + B)**", rv["total"]),
    rrow("Total, sólo costos de caja", rv["total_solo_caja"]),
], widths=[5.0, 2.0, 1.8, 1.8, 1.8, 1.9, 2.3], size=8.5)
T(["Escenario 2026 (test)", "Beneficio anual", "Inversión", "Recurrente", "ROI año 1", "ROI 3 años", "Recupero"], [
    rrow("A · Automatizar la lista con la regla (sin modelo)", rt["automatizacion_sin_modelo"]),
    rrow("B · Incremental del modelo", rt["incremental_modelo"]),
    rrow("**Total del flujo propuesto (A + B)**", rt["total"]),
], widths=[5.0, 2.0, 1.8, 1.8, 1.8, 1.9, 2.3], size=8.5)
P("La inversión de A excluye el desarrollo del modelo con su contingencia (USD 3.300) y su recurrente excluye el apoyo externo de "
  "reentrenamiento (USD 800), que se imputan a B. El escenario de referencia es **2025**: 2026 tiene cuatro veces más casos y viene "
  "de otro reporte, y se muestra como techo, no como expectativa.", 9.5)

H("7.4 Sensibilidad", 2)
T(["Cambio respecto de la base (escenario 2025)", "ROI 3 años del total", "Recupero"], [
    ["Base: valor por posición del E2, desarrollo USD 3.000", pct(rv["total"]["roi_3anios"]), f"{num(rv['total']['recupero_meses'])} meses"],
    [f"Desarrollo realista: 3 meses de un científico de datos (USD 18/h, {usd(rv['costo_desarrollo_3a4_meses'][0])} con contingencia)", pct(rv["total_desarrollo_3a4_meses"][0]["roi_3anios"]), f"{num(rv['total_desarrollo_3a4_meses'][0]['recupero_meses'])} meses"],
    [f"Desarrollo realista: 4 meses ({usd(rv['costo_desarrollo_3a4_meses'][1])})", pct(rv["total_desarrollo_3a4_meses"][1]["roi_3anios"]), f"{num(rv['total_desarrollo_3a4_meses'][1]['recupero_meses'])} meses"],
    ["Valor por posición del E1 (ARS 126.929)", pct(rv["total_valor_posicion_e1"]["roi_3anios"]), "No recupera"],
    ["Sólo costos de caja (mantenedor como costo de oportunidad)", pct(rv["total_solo_caja"]["roi_3anios"]), f"{num(rv['total_solo_caja']['recupero_meses'])} meses"],
], widths=[10.0, 3.2, 3.4])
P(f"El incremental del modelo es el más frágil: con un costo de desarrollo de 3 a 4 meses de un científico de datos su ROI a 3 "
  f"años en 2025 cae a {pct(rv['incremental_modelo_desarrollo_3a4_meses'][0]['roi_3anios'])} y "
  f"{pct(rv['incremental_modelo_desarrollo_3a4_meses'][1]['roi_3anios'])}. **El límite económico del caso** (observación de la "
  f"cátedra): con USD 80 a 134 de capital por posición, aun detectando bien, cada acierto vale entre USD 10 y 17. El proyecto rinde "
  f"por volumen y por las horas ahorradas, no por el valor de cada caso.")

H("7.5 Veredicto económico", 2)
P(f"**Viable con condiciones en el escenario de referencia (2025), sensible a dos supuestos.** El flujo propuesto recupera la "
  f"inversión en {num(rv['total']['recupero_meses'])} meses con un ROI a 3 años de {pct(rv['total']['roi_3anios'])}; el umbral de "
  f"equilibrio a 3 años es un beneficio de USD 9.150 por año y el escenario 2025 da {usd(rv['total']['beneficio_anual'])}. El "
  f"resultado se sostiene sobre todo por automatizar la lista; el modelo es una mejora con recupero de "
  f"{num(rv['incremental_modelo']['recupero_meses'])} meses que se justifica sólo si su costo de desarrollo se mantiene acotado. "
  f"**Corrección del E3:** se saca del veredicto el «recupero máximo de 12 meses», que no surgió de Casa Óga; el criterio que se "
  f"usa es ROI a 3 años ≥ 0, y queda a validar con Carlos F.")

# ================================================================== 8. LEGAL
H("8 · Factibilidad legal y regulatoria")
T(["Dimensión", "Score", "Riesgo principal", "Acción antes del go-live"], [
    ["Protección de datos personales (Ley 25.326)", "3", "No hay datos personales; el riesgo es ampliar a e-commerce", "Prohibir incorporar datos personales en fuentes y exportaciones"],
    ["Seguridad y control de accesos", "2", "Costos y condiciones de proveedores visibles para quien no los necesita", "Grupos de SharePoint: 28 vistas de tienda sin costos; costos sólo Compras y Finanzas; MFA y PC cifrada"],
    ["Conservación y trazabilidad", "2", "Transformaciones sin registro", "Guardar CSV originales, hash y bitácora del ETL; retención 5/3/1 años"],
    ["Contratos con externos (Leyes 24.766 y 11.723)", "2", "Sin NDA ni cláusulas de código", "Adenda: confidencialidad, uso limitado, titularidad del código y borrado de copias"],
    ["Explicabilidad del modelo", "2", "**Corresponde al bloque B (modelo).** El bloque A es la regla de cobertura y se explica sola", "Guardar score, versión, variables y decisión humana; prohibir liquidación automática"],
    ["**Promedio**", "**2,2**", "Viable con condiciones", "Las acciones son condición del piloto"],
], widths=[4.0, 1.2, 5.6, 5.8], size=8.5)
P("**Corrección del E3:** la explicabilidad se puntúa sobre la solución propuesta y no sólo sobre el modelo. Al pasar del ensamble "
  "a un único gradient boosting el bloque B también se vuelve más fácil de explicar; el score se mantiene en 2 por prudencia hasta "
  "verificar en el piloto que los motivos resultan claros para las tiendas.", 9.5)

# ================================================================== 9. RISKS
H("9 · Riesgos, dependencias y limitaciones")
P("**Corrección del E3:** los riesgos se construían sobre el escenario optimista; ahora todo se apoya en el escenario de "
  "referencia (2025).")
T(["Riesgo", "Prob.", "Impacto", "Mitigación concreta (qué se mide, quién, umbral)"], [
    ["Económico · el beneficio anual no alcanza los USD 9.150 que hacen viable el proyecto", "M", "A", "Carlos F. compara cada trimestre el valor registrado más las horas evitadas contra USD 2.288 por trimestre; si no se alcanza en dos trimestres, se reduce al bloque A."],
    ["Técnico · maestros sin la Ronda 3 y stock inválido", "A", "A", "Precondición: dataset v5 con la Ronda 3 y reevaluación. En cada corrida: 5 archivos, 0 claves desconocidas y 0 alertas con stock negativo."],
    ["Modelo · la ventaja sobre la regla desaparece", "M", "M", "El mantenedor compara a t+3 el flujo contra la cobertura a igual cupo; si no la supera en dos cohortes seguidas, se publica sólo el bloque A."],
    ["Entorno · cambio de régimen como 2026", "A", "M", "Mediana de cobertura, % sin venta y prevalencia contra la base 2025; desvío > 20% → alertas provisionales y ajuste del cupo por tramos."],
    ["Organizacional · sin mantenedor o baja adopción", "A", "A", "Precondición de go-live; % de alertas con acción registrada ≥ 60% en cada cierre (Lucía O.)."],
    ["Legal · difusión de costos", "M", "A", "Adenda y accesos por rol antes del primer acceso externo; prueba con un usuario de tienda."],
], widths=[5.2, 1.2, 1.4, 8.8], size=8.5)
H("9.1 Top 3 riesgos críticos", 2)
T(["Campo", "1 · Beneficio insuficiente", "2 · Datos inválidos o sin Ronda 3", "3 · Ventaja del modelo que no se sostiene"], [
    ["Por qué es crítico", f"El ROI 2025 es positivo ({pct(rv['total']['roi_3anios'])}) pero se vuelve negativo con un costo de desarrollo realista.", "El target y el capital se calculan con estos datos.", f"En 2026 el modelo agrega sólo {ft['flujo']['vp'] - ft['regla_mismo_cupo']['vp']} casos sobre la regla."],
    ["Señal", "Beneficio trimestral < USD 2.288", "Algún archivo ausente o claves desconocidas", "Flujo ≤ cobertura a igual cupo en dos cohortes"],
    ["Respuesta", "Quedarse con el bloque A, que concentra el valor", "No publicar las filas afectadas y corregir antes del cierre", "Publicar sólo el bloque A y reentrenar"],
], widths=[2.8, 4.6, 4.6, 4.6], size=8.5)
H("9.2 Dependencias y limitaciones", 2)
T(["Dependencia", "De quién", "Para qué", "Estado y fecha"], [
    ["Incorporar la Ronda 3 (22 costos, 11 duplicados, 4 multiproveedor, 6 aperturas)", "Compras entrega; Fleischer reconstruye", "Dataset v5 y reevaluación antes del piloto", "**Pendiente. Responsable: Matías Fleischer. Fecha: semana 2 de la fase 3.**"],
    ["Mantenedor nombrado", "Dirección (María G.)", "Primera corrida", "Pendiente; propuesto el analista del equipo de Sofía R."],
    ["Exportación estandarizada", "Sistemas, proveedor del POS", "Cada cierre", "POS cotizado; inventario manual"],
    ["Aprobación del target", "María G. y Carlos F.", "Protocolo del piloto", "Pendiente de firma"],
], widths=[5.2, 3.8, 3.6, 4.0], size=8.5)
P("**Limitaciones:** las métricas están calculadas sobre datos que Casa Óga ya corrigió en parte (Ronda 3); 2026 viene de otro "
  "reporte; no se estima el precio de liquidación ni el recupero real por acción; la capacidad de 15-25 intervenciones por tienda "
  "nunca se midió.", 9.5)

# ================================================================== 10. SOLUTION AND GO-LIVE
H("10 · Diseño de la solución y go-live")
H("10.1 Flujo de punta a punta", 2)
T(["Etapa", "Qué ocurre", "Frecuencia", "Responsable"], [
    ["Ingesta", "Exportación de Ventas, Stock, OC, Transferencias y Liquidaciones con clave fija; control de recepción.", "Días 1-3 del cierre", "Mantenedor y Sistemas (proyecto: Fleischer)"],
    ["Preparación", "Reglas del E2 y 60 variables al cierre de t; filas inválidas excluidas y listadas.", "Días 3-4", "Mantenedor"],
    ["Scoring", f"Bloque A: cobertura > 12, ordenada por capital. Bloque B: modelo, {kb} posiciones fuera de A (tramos de 50 que pagan).", "Día 4", "Mantenedor (proyecto: Volpato)"],
    ["Entrega", "Planilla y tablero por rol en SharePoint: cada tienda ve sus alertas sin costos, con motivo.", "Día 5", "Lucía O. (proyecto: Fasce)"],
    ["Decisión", "La tienda propone liquidar, transferir, frenar compras o desestimar con motivo; Comercial y Compras autorizan en 30 minutos.", "Mensual", "María G., Diego P.; coordina Lucía O."],
    ["Aprendizaje", "A t+3: precisión del último tramo, flujo contra regla a igual cupo, valor recuperado; ajuste del cupo y reentrenamiento.", "Mensual / trimestral", "Mantenedor; aprueba Carlos F."],
], widths=[2.4, 8.4, 2.6, 3.2], size=8.5)
H("10.2 Monitoreo", 2)
T(["Qué", "Indicador", "Umbral", "Acción"], [
    ["Datos de entrada", "Archivos, claves desconocidas, alertas con stock negativo", "< 5 archivos o > 0", "No publicar las filas afectadas"],
    ["Desempeño (cohortes maduradas)", "Recall del flujo y casos del flujo contra cobertura a igual cupo", "Flujo ≤ cobertura dos cohortes seguidas", "Sólo bloque A y reentrenar"],
    ["Cupo", "Precisión madurada del último tramo de 50", f"< {pct(vb['precision_equilibrio'])} → quitar un tramo; > 20% → probar uno más", "Ajustar el bloque B, nunca por encima de 700"],
    ["Segmento", "Recall por categoría, con IC 95%", "Categoría con el IC entero debajo del global (hoy: Cocina y mesa)", "Revisión manual de esa categoría"],
    ["Drift", "Mediana de cobertura, % sin venta, prevalencia", "Desvío > 20% contra 2025", "Alertas provisionales y reentrenamiento anticipado"],
    ["Adopción e impacto", "% de alertas con acción; valor + horas", "< 60%; < USD 2.288 por trimestre", "Revisar formato y cupo; reducir a bloque A"],
], widths=[3.0, 5.0, 4.4, 4.2], size=8.5)
H("10.3 Criterios de go-live", 2)
T(["Criterio", "Cómo se verifica", "Aprueba"], [
    ["Dataset v5 con la Ronda 3 y el flujo reevaluado: sigue superando a la regla a igual cupo en 2025 y 2026", "Log de la reevaluación (modelo_final_v4.py sobre v5)", "María G. con el responsable del modelo"],
    ["Corrida completa sobre un cierre real: 5 archivos, 0 claves desconocidas, 0 alertas con stock negativo", "Reporte de control de recepción", "Lucía O. y Sistemas"],
    ["Mantenedor nombrado (5-6 h por semana)", "Designación por escrito", "Dirección y Carlos F."],
    ["Adenda firmada, accesos por rol con MFA y PC cifrada", "Documento y prueba con un usuario de tienda", "Dirección, Sistemas y Diego P."],
    ["Protocolo de decisión humana aprobado y usuarios capacitados", "Acta del taller de 2 h", "Lucía O., María G. y Diego P."],
], widths=[7.2, 5.0, 4.4], size=8.5)
P("**Corrección del E3:** el criterio de desempeño ya no se da por cumplido con el test 2026 (un año fácil). La continuidad del "
  "modelo se decide con las cohortes maduradas del piloto: las alertas de cada mes se evalúan a los 3 meses, y el modelo sigue en "
  "el bloque B sólo si en las tres cohortes el flujo supera a la cobertura a igual cupo, en el cupo elegido y no en 600.", 9.5)

H(f"10.4 La primera lista: {DB_MES}", 2)
P(f"Para el último mes con datos, el modelo se reentrenó con todas las filas etiquetadas (mar-22 a may-26), con la misma "
  f"configuración elegida en 5.3, y puntuó las {num(DB['universo_mes']['posiciones'])} posiciones con stock del mes. El resultado está "
  f"en el tablero (3.6).")
T(["Indicador", "Valor"], [
    ["Alertas", f"{num(DB_N)}: {num(DB_A)} por la regla (bloque A) y {num(DB_N - DB_A)} por el modelo (bloque B)"],
    ["Capital a costo en alerta", f"ARS {num(DB_CAP / 1e6, 1)} M"],
    ["Dentro del cupo de las tiendas (25 por tienda)", f"{num(len(DB_IN))} alertas con ARS {num(DB_CAP_IN / 1e6, 1)} M ({pct(DB_CAP_IN / DB_CAP, 0)} del capital en alerta)"],
    ["Pasan al mes siguiente", f"{num(DB_N - len(DB_IN))} alertas, las de menor capital de cada tienda"],
    ["Acción sugerida", f"Transferir {num(DB_ACC['Transferir'])} · liquidar {num(DB_ACC['Liquidar'])}" + (f" · frenar compra {num(DB_ACC['Frenar compra'])}" if DB_ACC['Frenar compra'] else "") + (f" · frenar reposición {num(DB_ACC['Frenar reposición'])}" if DB_ACC['Frenar reposición'] else "")],
], widths=[6.0, 10.6], size=9)
BOX("Hallazgo: en 2026 la regla sola supera la capacidad de las tiendas", [
    f"El cupo de {kb} alertas del modelo se fijó con la validación 2025, cuando la regla marcaba ~{num(fv['bloque_a']['alertas_mes'])} "
    f"posiciones por mes. En {DB_MES} la regla sola marca {num(DB_A)}, por encima de las 700 que pueden trabajar 28 tiendas a 25 por mes. "
    f"Este mes manda la capacidad y no el valor de cada alerta: cada tienda trabaja primero las de más capital, que concentran el "
    f"{pct(DB_CAP_IN / DB_CAP, 0)} del total.",
    "**Decisión para la Dirección:** hay dos opciones. Una es una acción puntual de liquidación o transferencia para bajar el stock "
    "acumulado antes de empezar el piloto. La otra es aceptar que la lista tarde dos o tres meses en ponerse al día. En los dos casos, "
    "el bloque B mantiene su lugar: es lo único que anticipa los casos antes de que lleguen a 12 meses."])

# ================================================================== 11. VERDICT
BREAK()
H("11 · Veredicto integrado")
T(["Dimensión", "Veredicto", "Condición más crítica"], [
    ["Técnica", "Factibilidad media (2,25)", "Nombrar mantenedor antes del piloto"],
    ["Económica", f"Viable con condiciones en 2025: ROI a 3 años {pct(rv['total']['roi_3anios'])}, recupero {num(rv['total']['recupero_meses'])} meses", "Costo real de desarrollo y valor por posición"],
    ["Legal", "Viable con condiciones (2,2)", "Accesos por rol y adenda antes del primer acceso"],
    ["Riesgos", "Altos pero mitigables", "Que el beneficio no llegue a USD 9.150 por año"],
    ["Modelo", f"Supera a la regla a igual cupo en 2025 y 2026; rango de recall {pct(fv['flujo']['recall'], 0)}-{pct(ft['flujo']['recall'], 0)}", "Que la ventaja se sostenga en cohortes maduradas"],
], widths=[2.6, 8.0, 6.0])
BOX("Veredicto: VIABLE CON CONDICIONES COMO PILOTO SUPERVISADO", [
    f"Recomendamos avanzar con un piloto de tres cierres sobre la infraestructura existente. La lista automatizada con la regla ya "
    f"justifica el esfuerzo en un año como 2025 y el modelo agrega {fv['flujo']['vp'] - fv['regla_mismo_cupo']['vp']} casos sobre la "
    f"regla a igual cupo, con ~{num(fv['flujo']['alertas_mes'])} alertas por mes. En 2026 la regla sola ya supera la capacidad de "
    f"las tiendas ({num(DB_A)} posiciones en {DB_MES}), así que la lista se prioriza por capital (10.4).",
    "**Tres acciones antes de empezar:** (1) nombrar al mantenedor y firmar la adenda de confidencialidad con accesos por rol; "
    "(2) estandarizar la exportación mensual; (3) reconstruir el dataset con la Ronda 3 y repetir la evaluación.",
    "**Riesgo residual:** que la ventaja del modelo sobre la regla sea chica en la práctica, como en 2026. Si pasa, el proyecto "
    "sigue siendo útil con el bloque A y el ahorro de horas, y el modelo se retira sin costo hundido adicional."])

# ================================================================== 12. CHANGES
H("12 · Cambios respecto de lo entregado")
P("Cada fila indica qué decía la entrega original, qué dice este documento y qué devolución lo motivó (cátedra o Casa Óga).")
H("12.1 Entregable 1", 2)
T(["#", "Sección", "Qué decía", "Qué dice ahora", "Motivo"], [
    ["1", "Problem statement y 5.3", "Dos juegos de cifras: 661 pos. / $83,9 M y 8,86% → 7,93% / $41,4 M → $93,1 M", "Un solo indicador reproducible: cobertura > 12 meses; 866 posiciones y ARS 178,6 M en ago-26 (1.4)", "Cátedra: cifras que no cierran (prioridad alta)"],
    ["2", "Problem statement", "Crecimiento del capital presentado como deterioro", "Estable en proporción 2023-2025; el salto es de 2026, con parte atribuible al nuevo reporte (1.4)", "Cátedra: narrativa alarmista"],
    ["3", "Parte C · fases", "Sin backlog", "Backlog inicial con épicas, historias y prioridad MoSCoW (3.3)", "Cátedra: el título prometía backlog"],
    ["4", "1.3 Proceso", "Describía el objetivo del proyecto", "Proceso vigente de gestión de rotación y liquidación (1.3)", "Cátedra: proceso ≠ objetivo"],
    ["5", "1.2 Mercado", "Sin fuente externa; estacionalidad 143/61", "INDEC y CAME citados; sin estacionalidad tras ajustar tendencia (1.2)", "Cátedra; hallazgo del EDA (D1)"],
    ["6", "2.4 Stakeholders", "Una columna de influencia; tiendas con influencia baja", "Influencia técnica y de decisión separadas (2.3)", "Cátedra"],
    ["7-8", "3.1-3.2 Restricciones", "Calidad de datos, alcance e IT como tecnológicas; disponibilidad como temporal", "Reclasificadas: organizacional, RRHH, alcance y hallazgo (2.4)", "Cátedra"],
    ["9", "Alcance", "Dashboard leíble como herramienta en vivo", "Corte mensual que se regenera en cada cierre (3.2)", "Cátedra"],
    ["10", "Visión", "Anticipación atribuida al semáforo", "La anticipa el modelo; el semáforo es el presente (3.1)", "Clase 7"],
    ["11", "Objetivos", "Rangos con condicionales", "Mínimo exigible o «no medible aún» (2.2)", "Clase 7"],
    ["12", "Stakeholders", "Sin Sistemas/IT ni proveedores", "Incorporados, con fuente de cada expectativa (2.3)", "Clase 7"],
    ["13", "Dashboard", "Tablero descriptivo con corte dic-2025", f"Tablero por área con la lista del modelo para {DB_MES}, filtros y descarga (3.6, 10.4)", "Clase 7"],
    ["D", "Varias", "«Ticket medio»; cobertura 10,6 → 5,2; datasets «no recibidos»", "Precio medio por unidad; cobertura estable; 15 fuentes disponibles (1.1, 4.1)", "Hallazgos del EDA del E2"],
], widths=[0.8, 2.4, 4.4, 5.6, 3.4], size=8)
H("12.2 Entregable 2", 2)
P("Las once correcciones de Casa Óga y de la cátedra se aplicaron en la versión 3.0 del consolidado del E2 (detalle en "
  "`Entregable 2/Correcciones-Feedback-Grupo-1.md`): ritmo de venta definido, fuentes por análisis, fila «Caída de 2026» partida, "
  "criterios antes del mapa, Calendario en amarillo, fundamento de los amarillos, H13 y 2026 como otra fuente, deduplicación de "
  "Casa Óga, «sin rotación» fuera del neteo, plazos por acción, capital por categoría y cobertura sin winsorizar. Resultado: "
  "**dataset v4**. En este informe:")
T(["Sección", "Cambio", "Motivo"], [
    ["Modelo (5)", "Se reentrena sobre la v4 (el E3 usaba la v3)", "E2: decidir la versión; una cifra, un valor"],
    ["5.2-5.5", "Regla y modelo en validación 2025 y test 2026 por separado; desempeño como rango", "E2 §2.1 y fila «Dataset entregado»"],
], widths=[3.0, 8.6, 5.0])
H("12.3 Entregable 3", 2)
T(["Sección E3", "Qué decía", "Qué dice ahora", "Motivo (devolución)"], [
    ["Entrega", "Sólo el PDF", "Informe, scripts, resultados, planilla y gráficos en la carpeta «Entregable 4» del repositorio", "Cátedra · 0"],
    ["1.4-1.5", "Calendario hasta dic-25; pedía Calendario y 22 costos", "Calendario a ago-26; pedidos quitados; ×1,2321 sólo para v4 (4.1)", "Casa Óga y cátedra · 1.4"],
    ["1.5 / 6.4", "Ronda 3 como limitación, sin fecha", "Precondición con responsable y fecha; criterio de go-live (3.4, 9.2, 10.3)", "Cátedra · 1.1 y 6"],
    ["1.6", "PC de USD 1.000 como nota", "PC de oficina existente, confirmada (6)", "Cátedra · 1.6"],
    ["2.1-2.3", "Sin exclusión t+3 ni sensibilidad a reglas", "Incorporadas desde el E2 (4.3)", "Cátedra · 2.1"],
    ["2.4", "Tres métricas distintas", "Una métrica: recall y valor en el cupo; PR-AUC secundaria (5.1)", "Cátedra · 2.4"],
    ["4.2", "Sin métrica en entrenamiento", "Train, validación y test en la misma tabla (5.2)", "Cátedra · 4.1"],
    ["3.2", "Desarrollo USD 3.000 sin sensibilidad; mantenedor sin aclarar", "Sensibilidad de 3-4 meses de un científico de datos; mantenedor como costo de oportunidad (7.1, 7.4)", "Casa Óga y cátedra · 3.2"],
    ["3.3-3.6", "Valor del E1 (ARS 126.929); un solo ROI; payback de 12 meses", "Valor del E2 (ARS 208.730); dos ROI; criterio ROI a 3 años ≥ 0 (7.2-7.5)", "Cátedra · 3.3"],
    ["4.4-4.5", "Incremental contra la regla forzada a 600", "Contra la regla de la línea base y a igual cupo (5.5, 7.3)", "Cátedra · 4.4"],
    ["7.1", "Ensamble elegido sobre la validación 2025", "Gradient boosting elegido en la validación interna 2024 (5.3)", "Cátedra · 7.1"],
    ["7.2 / 9", "600 alertas por mes", f"Cupo por valor: regla + {kb} del modelo, en tramos de 50 (5.4)", "Casa Óga y cátedra · 7.2 y 9"],
    ["7.3", "Importancia de LightGBM", "Importancia por permutación del modelo final (5.6)", "Cátedra · 7.3"],
    ["7.4", "Patagonia «peor» sin intervalo", "IC 95% de Wilson para regiones y categorías (5.6)", "Cátedra · 7.4"],
    ["8.2", "Sin explicar por qué 2026 es fácil", f"Persistencia sin venta: {pct(pers['2025']['proporcion'])} → {pct(pers['2026']['proporcion'])} (5.5)", "Cátedra · 8"],
    ["5.3", "Explicabilidad 2 por el ensamble", "Aclarado: corresponde al bloque B (8)", "Cátedra · 5"],
    ["6.1-6.3", "Escenario optimista", "Escenario de referencia 2025; riesgo 1 = no llegar a USD 9.150 (9)", "Casa Óga y cátedra · 6"],
    ["10.3", "Recall@600 ≥ 60% en test, ya cumplido", "Cohortes maduradas del piloto, en el cupo elegido (10.3)", "Cátedra · 10"],
    ["Cifras", f"Recall 71%-77% (v3, ensamble, 600); ROI −16,6% a −1,7%", f"Recall {pct(fv['flujo']['recall'], 0)}-{pct(ft['flujo']['recall'], 0)} (v4, gradient boosting, ~{num(fv['flujo']['alertas_mes'])} alertas); ROI 2025 {pct(rv['total']['roi_3anios'])}", "Consecuencia de los cambios anteriores"],
], widths=[2.0, 4.4, 6.4, 3.8], size=8)

# ================================================================== ANNEX
H("Anexo · Fuentes externas y reproducibilidad")
P("[1] INDEC, Intercambio Comercial Argentino, datos de 2025, según La Gaceta (importaciones 2025: +24,7%, USD 75.791 M) y Revista "
  "Mercado (bienes de consumo, dic-2025: +17,1% interanual). "
  "lagaceta.com.ar/nota/1122164/economia/importaciones-argentinas-crecieron-247porciento-2025.html · "
  "mercado.com.ar/informes-especiales/el-superavit-comercial-se-achica-mientras-repuntan-las-importaciones", 9)
P("[2] CAME, Índice de ventas minoristas pymes, nov. y dic. 2025, según El Cronista y Diario de Cuyo. "
  "cronista.com/economia-politica/ventas-minoristas-pyme-cayeron-41-en-noviembre-que-rubros-se-hundieron-y-cual-resistio-la-crisis · "
  "diariodecuyo.com.ar/economia/las-ventas-en-comercios-minoristas-cayeron-52-en-diciembre-1819267.html", 9)
T(["Qué", "Archivo en el repositorio"], [
    ["Modelo final, valor, ROI, importancia, segmentos y persistencia", "Entregable/Entregable 4/Modelo/modelo_final_v4.py → resultados/modelo_final_v4_resultados.json y _log.txt"],
    ["Gráficos de este informe", "Entregable/Entregable 4/Informe/graficos_informe.py → graficos/"],
    ["Tablero y lista del mes", "Entregable/Entregable 4/Dashboard/preparar_datos_dashboard.py y armar_dashboard.py → Casa-Oga-Dashboard.html (filas del mes: construir_dataset_modelo.py con EXPORTAR_SCORING=1)"],
    ["Este documento", "Entregable/Entregable 4/Informe/armar_informe_final.py"],
    ["Dataset v4 y diccionario", "Datasets_Modelo/dataset_entrenamiento_v4*.parquet y diccionario_features_v4.csv"],
    ["Limpieza y construcción del dataset", "Entregable/Entregable 2/EDA/criterios_limpieza.py y Modelo/construir_dataset_modelo.py"],
    ["Entregas anteriores", "Entregable/Entregable 1, 2 y 3 (documentos originales sin modificar)"],
], widths=[5.6, 11.0], size=8.5)

doc.save(OUTDOC)
print("OK", OUTDOC)
