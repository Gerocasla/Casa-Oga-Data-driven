# -*- coding: utf-8 -*-
"""Genera los archivos del deck (Slides artifact) en Presentacion/deck/project/."""
import os, json, datetime
BASE = os.path.dirname(os.path.abspath(__file__)); E2 = os.path.dirname(BASE)
OUT = os.path.join(BASE, "deck", "project"); os.makedirs(os.path.join(OUT, "slides"), exist_ok=True)
I = json.load(open(os.path.join(E2, "Modelo", "resultados", "insights.json"), encoding="utf-8"))
C26 = json.load(open(os.path.join(E2, "EDA", "resultados", "cambio_2026.json"), encoding="utf-8"))   # graficos_presentacion.py
IMG = {"venta": "/_blob/3c2223f1d1c6339c830ee806884f8f61", "estac": "/_blob/43c6981580a79beb1efb8097927605a1",
       "cobdef": "/_blob/b86da51072ea5789fd601d99c350ca93", "v2526": "/_blob/b58994c3ddc7a35522592cd3d9b3ddac",
       "cola": "/_blob/d8a92d1eff15dc35bd290d5587c533b5", "prev": "/_blob/7905fa8d85c212d9ad87118976873099",
       "cap": "/_blob/19331e5df80e782e71bbf913d9c492d9", "senal": "/_blob/2d7fd4a01dc83c89b21d974d6364c15d",
       "ad": "/_blob/bdc99ef4d31e9129611313178b39539e", "caprojo": "/_blob/e786bd0172083880f96c23d1f3375cf5",
       "catalogo": "/_blob/a1c11e0000000000000000000000c011", "sinventa": "/_blob/a1c12e0000000000000000000000c012"}

DARK, LIGHT, ALT, INK, BODY, MUT = "#14213D", "#FBFBF8", "#F1F2F6", "#14213D", "#3D4656", "#5B6475"
BLUE, ORANGE, GOLD, LINE = "#2F5E96", "#C4470A", "#F5B800", "#D9DDE4"
HF = "font-family:'DM Sans', Arial, sans-serif"
BF = "font-family:'IBM Plex Sans', Arial, sans-serif"
RS = I["resumen"]; SP_ = RS["split"]
MES = {"Jan": "ene", "Feb": "feb", "Mar": "mar", "Apr": "abr", "May": "may", "Jun": "jun", "Jul": "jul", "Aug": "ago", "Sep": "sep", "Oct": "oct", "Nov": "nov", "Dec": "dic"}
fm = lambda s: MES[s[:3]] + s[3:]
n = lambda v, d=1: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

slides = []; sections = {}
def add(sid, html, notes="", section=None):
    if section: sections[f"sec{len(sections)+1}"] = {"description": section, "start": sid}
    body = html.replace("{{NOTES}}", f"<aside>{notes}</aside>" if notes else "")
    slides.append((sid, body))

def page(sid, eyebrow, title, inner, notes="", bg=LIGHT, section=None, gap=40):
    num = len(slides) + 1
    html = (f'<section id="{sid}" data-transition="fade" style="background:{bg}; color:{INK}; {BF}; padding:112px 128px 160px; '
            f'display:flex; flex-direction:column; gap:{gap}px">'
            f'<div style="display:flex; flex-direction:column; gap:12px">'
            f'<p style="font-size:24px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{BLUE}">{eyebrow}</p>'
            f'<h2 style="{HF}; font-size:60px; font-weight:700; line-height:1.1; color:{INK}">{title}</h2></div>'
            f'{inner}'
            f'<p style="position:absolute; left:128px; bottom:64px; width:1664px; font-size:24px; color:{MUT}">Casa Óga · Entregable 2 · Grupo 1 &#160;·&#160; {num}</p>'
            '{{NOTES}}</section>')
    add(sid, html, notes, section)

def divider(sid, num, title, sub, section):
    html = (f'<section id="{sid}" data-transition="fade" style="background:{DARK}; color:{LIGHT}; {BF}; padding:128px; display:flex; flex-direction:column; justify-content:center; gap:32px">'
            f'<div style="width:120px; height:8px; background:{GOLD}"></div>'
            f'<p style="font-size:32px; font-weight:600; color:{GOLD}; letter-spacing:2px">{num}</p>'
            f'<h1 style="{HF}; font-size:96px; font-weight:700; line-height:1.05; color:{LIGHT}">{title}</h1>'
            f'<p style="font-size:36px; color:#C9D2E3; line-height:1.4; width:1300px">{sub}</p>{{{{NOTES}}}}</section>')
    add(sid, html, "", section)

def chart(src, alt, side, w=1120, h=518):
    return (f'<div style="display:flex; gap:56px; align-items:center; flex:1">'
            f'<img src="{src}" alt="{alt}" style="width:{w}px; height:{h}px; object-fit:contain; border-radius:12px">'
            f'<div style="flex:1; display:flex; flex-direction:column; gap:28px">{side}</div></div>')

def stat(big, txt, color=INK):
    return (f'<div style="display:flex; flex-direction:column; gap:6px; border-left:6px solid {GOLD}; padding:4px 0 4px 24px">'
            f'<p style="{HF}; font-size:52px; font-weight:700; line-height:1.05; color:{color}">{big}</p>'
            f'<p style="font-size:26px; line-height:1.35; color:{BODY}">{txt}</p></div>')

def card(title, body, extra_style=""):
    return (f'<div style="flex:1; display:flex; flex-direction:column; gap:12px; background:#FFFFFF; border:1px solid {LINE}; '
            f'border-radius:16px; padding:32px; {extra_style}"><h3 style="{HF}; font-size:32px; font-weight:700; line-height:1.15; color:{INK}">{title}</h3>'
            f'<p style="font-size:24px; line-height:1.4; color:{BODY}">{body}</p></div>')

def table(head, rows, widths, fs=24):
    h = "".join(f'<th style="width:{w}%; font-size:{fs}px">{c}</th>' for c, w in zip(head, widths))
    r = "".join('<tr>' + "".join(f'<td>{c}</td>' for c in row) + '</tr>' for row in rows)
    return (f'<table style="width:1664px; font-size:{fs}px; color:{BODY}; border-collapse:collapse; padding:10px">'
            f'<tr style="background:#E7EBF2">{h}</tr>{r}</table>')

# ================================================================= 1 PORTADA / INTRO
add("portada", f'''<section id="portada" style="background:{DARK}; color:{LIGHT}; {BF}; padding:128px; display:flex; flex-direction:column; justify-content:space-between">
<div style="display:flex; flex-direction:column; gap:28px">
<p style="font-size:28px; font-weight:600; letter-spacing:3px; color:{GOLD}">FACTIBILIDAD DE PROYECTOS DATA DRIVEN · ENTREGABLE 2</p>
<h1 style="{HF}; font-size:112px; font-weight:700; line-height:1.02; color:{LIGHT}; width:1500px">Del dato crudo al dataset de entrenamiento</h1>
<p style="font-size:40px; line-height:1.35; color:#C9D2E3; width:1400px">Casa Óga · riesgo de dead stock por SKU y tienda · datos a agosto de 2026</p></div>
<div style="display:flex; flex-direction:column; gap:12px"><div style="width:160px; height:8px; background:{GOLD}"></div>
<p style="font-size:28px; color:#C9D2E3">Grupo 1 · Gerónimo Fasce · Gianfranco Di Claudio · Matías Fleischer · Simón Volpato Escandarani · Santiago Hernández</p></div>
{{{{NOTES}}}}</section>''', "Presentamos el Entregable 2: qué encontramos en los datos, cómo los limpiamos, qué vamos a predecir y con qué dataset.", "Qué hicimos y qué muestra la presentación")

page("recorrido", "Recorrido", "Cuatro preguntas, en este orden",
 '<div style="display:grid; grid-template-columns:repeat(2, 1fr); gap:28px; flex:1">'
 + card("1 · ¿Qué dicen los datos?", "EDA de las 15 fuentes al corte ago-2026. Qué se confirma del TP1, qué no, y qué cambió en 2026.")
 + card("2 · ¿Se puede confiar en ellos?", "Mapa de calidad, 12 hallazgos, los criterios acordados con el negocio y cuánto cambia el análisis al corregir.")
 + card("3 · ¿Qué vamos a predecir?", "La variable objetivo, por qué esa y no otra, y qué tan sólida es cada decisión detrás.")
 + card("4 · ¿Con qué datos?", f"El dataset de entrenamiento: {RS['n_num']+RS['n_cat']} variables sin leakage, las que quedaron afuera y por qué, y si tiene señal.")
 + '</div>', "Estructura: diagnóstico, limpieza, target y dataset. Todo lo que mostramos se reproduce con los scripts del repo.")

page("partida", "Punto de partida", "15 fuentes y 56 meses de datos",
 '<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:48px">'
 + stat("15", "fuentes: ventas, stock, catálogo, OC, promociones y más")
 + stat("299.400", "filas mes · tienda · SKU en Ventas y en Stock") + stat("56", 'meses, de <span style="white-space:nowrap">ene-2022</span> a <span style="white-space:nowrap">ago-2026</span>') + stat("800 × 28", "SKUs × tiendas") + '</div>'
 + f'<div style="display:flex; flex-direction:column; align-items:center; gap:8px">'
 f'<img src="{IMG["v2526"]}" alt="Venta mensual 2025 contra 2026, enero a agosto" style="width:860px; height:398px; object-fit:contain">'
 f'<p style="font-size:30px; color:{BODY}"><b style="{HF}; font-size:44px; color:{ORANGE}">−13,2%</b>&#160; venta ene-ago 2026 contra 2025</p></div>',
 "Los datos de 2026 llegaron después; verificamos que no cambiaran el histórico. El dato nuevo es la caída de la venta: en la próxima diapositiva, de dónde sale.")

# ================================================================= 2 EDA
divider("d-eda", "PARTE 1", "Qué dicen los datos", "EDA al corte ago-2026: crecimiento, estacionalidad, cobertura y el cambio de 2026.", "EDA: qué se confirma, qué no y qué cambió en 2026")
page("crecimiento", "EDA · evolución", "El negocio creció sumando posiciones, no vendiendo más por posición",
 chart(IMG["venta"], "Venta neta mensual en millones de pesos y unidades por posición, enero 2022 a agosto 2026",
  stat("$40.083 M", "vendidos entre ene-2022 y ago-2026, con devoluciones neteadas")
  + stat("17 → 8.073", "posiciones SKU–tienda con venta entre ene-22 y dic-25")
  + stat("~3,2", "unidades por posición y mes, planas todo el período (línea punteada)")),
 "La línea azul es la venta; la punteada naranja, unidades por posición. El crecimiento es de amplitud del catálogo y la red. En 2026 la venta cae (franja amarilla).")
page("tp1", "EDA · correcciones al TP1", "Dos cifras del TP1 que no se sostienen con los datos",
 '<div style="display:flex; gap:48px; flex:1">'
 f'<div style="flex:1; display:flex; flex-direction:column; gap:20px"><img src="{IMG["estac"]}" alt="Índice estacional por mes, cálculo del TP1 contra ajustado por tendencia" style="width:808px; height:374px; object-fit:contain; border-radius:12px">'
 f'<h3 style="{HF}; font-size:34px; font-weight:700">No hay estacionalidad</h3><p style="font-size:26px; line-height:1.4; color:{BODY}">El «143 en diciembre vs 61 en enero» era el crecimiento del año. Ajustado por tendencia, todos los meses quedan entre 98 y 106.</p></div>'
 f'<div style="flex:1; display:flex; flex-direction:column; gap:20px"><img src="{IMG["cobdef"]}" alt="Cobertura de inventario según tres definiciones, 2023 a 2026" style="width:808px; height:374px; object-fit:contain; border-radius:12px">'
 f'<h3 style="{HF}; font-size:34px; font-weight:700">La cobertura no «mejoró»: está estable</h3><p style="font-size:26px; line-height:1.4; color:{BODY}">El 10,6 → 5,2 del TP1 sale solo de dividir por un promedio de 12 meses que incluye el arranque de 2022. Con cualquier otra medida: ~5,2 meses todo el período.</p></div></div>',
 "Esto corrige el TP1 y va al consolidado. También baja la narrativa alarmista que marcó la cátedra: la cobertura estaba estable.")
vv = I["venta_25_26"]; dv = [b / a - 1 for a, b in zip(vv["v2025"], vv["v2026"])]
page("caida", "EDA · 2026", "2026: la venta cae y el stock no acompaña",
 chart(IMG["v2526"], "Venta mensual 2025 contra 2026, enero a agosto",
  stat("−13,2%", "venta ene-ago 2026 contra el mismo período de 2025 (unidades −12,7%, posiciones −8,1%)")
  + stat(f"{n(min(dv)*100,0)}% → {n(max(dv)*100,0)}%", "la caída es de nivel: arranca fuerte en enero y se achica mes a mes")
  + f'<p style="font-size:24px; line-height:1.4; color:{MUT}">Comparación en bruto: 2026 no trae devoluciones registradas, netear solo 2025 la sesgaría.</p>'),
 "Primer año de caída después de tres de crecimiento. Todavía no figura en ningún documento anterior y explica buena parte de lo que pasa con el target.")
al = C26["altas_por_anio"]
page("catalogo", "EDA · 2026 · de dónde sale la caída", "Dos tercios de la caída vienen de productos que ya no están",
 chart(IMG["catalogo"], "Variación mensual de la venta 2026 contra 2025: total y solo los SKUs que siguen vendiendo",
  stat("2 de cada 3", f"pesos de la caída ene-ago (${n(C26['baja_M'],0)} M de ${n(C26['gap_M'],0)} M) son los {C26['skus_baja']} SKUs discontinuados a fin de 2025: {n(C26['baja_pp'])} de los {n(-C26['var_total'])} puntos")
  + stat(f"{n(C26['var_sigue'])}%", f"en los {C26['skus_sigue']} SKUs que siguen: de {n(C26['var_sigue_mes'][0],0)}% en enero a {n(C26['var_sigue_mes'][-1],0)}% en agosto")
  + stat("0 altas", f"ningún SKU nuevo desde {fm(datetime.date.fromisoformat(C26['ultima_alta']).strftime('%b-%y'))} (entre {min(al.values())} y {max(al.values())} por año hasta 2025)")
  + f'<p style="font-size:24px; line-height:1.4; color:{MUT}">El target excluye los discontinuados: la caída que ve el modelo es la línea azul.</p>'),
 "El negocio creció sumando productos. A fin de 2025 dio de baja 96 y en 2026 no sumó ninguno: la caída es de surtido, no de demanda general. "
 "En los productos que siguen, la venta ya volvió casi al nivel de 2025. Esto matiza la diapositiva anterior.")
rm = I["rojo_mes"]; r0 = rm["meses"].index("2025-12"); cp = I["cobertura_pct"]; i0 = cp["meses"].index("2025-12")
page("cola", "EDA · cobertura por posición", "El promedio esconde el problema: la cola se engorda",
 chart(IMG["cola"], "Percentiles 50, 90 y 99 de la cobertura por posición, 2023 a 2026",
  stat(f"{n(cp['p50'][-1])} meses", "mediana de cobertura: no se mueve en todo el período")
  + stat(f"{n(cp['p99'][i0],0)} → {n(cp['p99'][-1],0)}", "meses en el percentil 99 entre dic-25 y ago-26")
  + stat(f"{n(rm['posiciones'][r0],0)} → {n(rm['posiciones'][-1],0)}", f"posiciones con más de 12 meses de stock; ${n(rm['capital'][-1])} M a costo en ago-26")
  + f'<p style="font-size:24px; line-height:1.4; color:{MUT}"><b>Por qué:</b> no es la caída general (dos tercios son SKUs dados de baja, fuera del target). Es un grupo de posiciones que dejó de vender a comienzos de 2026 y no se liquidó.</p>'),
 "Si miráramos el promedio diríamos que no pasa nada. El riesgo está en pocas posiciones que acumulan años de stock. Eso es lo que el target tiene que capturar.")

lq_, ls_, oc_ = C26["liq"], C26["liq_sobrestock"], C26["oc_activos_ene_jul"]
page("sinventa", "EDA · 2026 · qué cambió en la operación", "Las posiciones sin venta crecen 2,5 veces en un trimestre y casi no se liquidan",
 chart(IMG["sinventa"], "Posiciones con stock y sin venta en 3 meses por mes, 2024 a 2026, y liquidaciones de enero a agosto por año",
  stat(f"{C26['sin_venta_dic25']} → {C26['sin_venta_fin']}", f"posiciones activas con stock y sin ninguna venta en 3 meses (dic-25 → ago-26); ${n(C26['capital_dic25'])} M → ${n(C26['capital_fin'])} M a costo")
  + stat(f"{n((lq_['2026']/lq_['2025']-1)*100,0)}%", f"liquidaciones ene-ago contra 2025 ({lq_['2025']} → {lq_['2026']}); por sobrestock, {ls_['2025']} → {ls_['2026']}")
  + stat(f"{C26['sin_venta_liquidadas_2026']} de {C26['sin_venta_fin']}", "posiciones sin venta tuvieron alguna liquidación en 2026")
  + f'<p style="font-size:24px; line-height:1.4; color:{MUT}">Las compras de estos SKUs no se movieron: {n((oc_["2026"]/oc_["2025"]-1)*100)}% en unidades ene-jul.</p>'),
 "Es un salto, no una deriva: pasa entre enero y marzo de 2026 y después se estabiliza. Al mismo tiempo, la palanca que vacía estas posiciones se usa la mitad. "
 "Explica buena parte del 9% de prevalencia de 2026. Para el modelo, el test 2026 viene de una operación distinta: hay que vigilarlo como cambio de régimen. "
 "Pregunta para el negocio: ¿por qué bajaron las liquidaciones en 2026?")

# ================================================================= 3 CALIDAD
divider("d-cal", "PARTE 2", "Calidad y limpieza", "Qué está mal, cómo lo tratamos, por qué, y cuánto cambia el resultado al corregir.", "Calidad: hallazgos, criterios de limpieza y su impacto")
# Criterio: Critico = sin tratarlo cambia un KPI, el target o una feature, deja una variable afuera, o usarlo exige un
# supuesto o confirmacion del negocio. Menor = existe pero no cambia ningun resultado. OK = sin problemas detectados.
MAPA = [("Ventas", "V R R V R R A"), ("Stock tiendas", "V R R V R R A"), ("Catálogo", "R A V R V R R"), ("Tiendas", "V R R V V V V"),
        ("Calendario", "V V V R V V V"), ("Liquidaciones", "V R A V A V V"), ("Devoluciones", "V V V R V V V"), ("Historial precios", "A R A V V V R"),
        ("Órdenes de compra", "V V V V V V V"), ("Presupuesto", "A R A V A V A"), ("Promociones", "A A A V A A A"), ("Proveedores", "V V V V V V V"),
        ("Stock depósito", "V A V V V V V"), ("Transferencias", "V A V V V V V"), ("Costo almacenam.", "V A V A V V A")]
COL = {"V": ("#D8F0DF", "#1E5B32", "OK"), "A": ("#FCEFC7", "#6B4E00", "Menor"), "R": ("#F8D3D3", "#8A1C1C", "Crítico")}
cells = "".join(f'<p style="font-size:22px; font-weight:700; color:{MUT}; padding:2px 8px">{h}</p>' for h in ["Fuente", "Complet.", "Consist.", "Exactitud", "Actualidad", "Validez", "Unicidad", "Trazab."])
for f, vals in MAPA:
    cells += f'<p style="font-size:22px; color:{INK}; padding:0 8px">{f}</p>'
    for v in vals.split():
        bgc, fg, t = COL[v]
        cells += f'<p style="font-size:22px; font-weight:600; color:{fg}; background:{bgc}; padding:0 8px; border-radius:6px; text-align:center">{t}</p>'
CRIT = [("V", "no se detectó ningún problema (los nulos esperables no cuentan)."),
        ("A", "el problema existe pero no cambia ningún resultado: pocos registros que se excluyen, un campo que no se usa o una corrección mecánica."),
        ("R", "sin tratarlo cambia un KPI, el target o una variable del modelo, o usar el dato exige un supuesto o la confirmación del negocio.")]
leyenda = '<div style="display:flex; gap:24px">' + "".join(
    f'<p style="flex:1; font-size:21px; line-height:1.35; color:{BODY}"><b style="color:{COL[k][1]}; background:{COL[k][0]}; padding:0 8px; border-radius:6px">{COL[k][2]}</b> {t}</p>'
    for k, t in CRIT) + '</div>'
page("mapa", "Calidad · diagnóstico", "Mapa de calidad: 15 fuentes × 7 dimensiones",
 f'<div style="display:grid; grid-template-columns:320px repeat(7, 1fr); gap:3px">{cells}</div>' + leyenda,
 "El criterio es el impacto en el uso, no la cantidad de errores. Crítico: si no se trata cambia un resultado o hay que asumir algo para usar el dato (duplicados, negativos, 22 SKUs sin costo, fuentes sin 2026, historial reconstruido). Menor: existe pero no mueve nada (5 descuentos y 4 promociones inválidas que se excluyen, variantes de categoría que se unifican con una regla). El desvío de stock en tránsito se asigna a Stock, no a Transferencias, cuyas cifras se usan tal cual.", gap=16)
H1 = [("H1 · Claves duplicadas", "2.378 en Ventas y en Stock, solo 2022-25.", "Conservar la 1ra ocurrencia. Causa raíz: H2."),
      ("H2 · SKUs duplicados", "15 SKUs cargados dos veces, difieren solo en proveedor.", "Error del sistema (P11). Costo único de catálogo."),
      ("H3 · Venta antes de abrir", "6 tiendas, 11.058 filas, $1.471,7 M.", "Sin respuesta. No usar antigüedad de tienda."),
      ("H4 · Negativos imposibles", "2.317 ventas y 1.209 stocks negativos.", "Stock: piso en 0 (P16). Ventas: netear devoluciones (P23)."),
      ("H5 · Venta sin stock", "1.020 filas con venta y stock 0; 187 en 2026.", "Misma causa que H4: desfase POS–inventario."),
      ("H6 · Tránsito sin conciliar", "8.771 uds vs 936 de transferencias (9×).", "Campo sin definición: queda fuera del modelo.")]
H2 = [("H7 · Liquidaciones incoherentes", "90 de 108 «Discontinuación» sobre SKUs activos; tienda «Todas».", "Se usan solo como historia hasta t."),
      ("H8 · Precios vs historial", "Precio de venta > 1,5× el histórico en 33% de filas.", "Historial reconstruido (P9-P10): no se usa."),
      ("H9 · Descuentos y presupuesto", "5 descuentos fuera de 0-100%; 309 ceros y 3 negativos.", "Excluir del margen y del desvío (P28, P32)."),
      ("H10 · Promociones inválidas", "Ids repetidos y 2 con fin antes del inicio.", "Se excluyen del cálculo de promociones."),
      ("H11 · 22 SKUs sin costo", "No se puede valuar su stock ni su margen.", "Costo de OC × 1,2321, supuesto declarado."),
      ("H12 · Fuentes sin 2026", "Devoluciones, Calendario y catálogo cortan en 2025.", "Se declara; no se usan como features.")]
def hcards(items):
    return ('<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:24px; flex:1">' + "".join(
        f'<div style="display:flex; flex-direction:column; gap:10px; background:#FFFFFF; border:1px solid {LINE}; border-top:6px solid {BLUE}; border-radius:12px; padding:28px">'
        f'<h3 style="{HF}; font-size:30px; font-weight:700; line-height:1.15">{t}</h3><p style="font-size:24px; line-height:1.4; color:{BODY}">{m}</p>'
        f'<p style="font-size:24px; line-height:1.4; color:{INK}"><b>Tratamiento:</b> {tr}</p></div>' for t, m, tr in items) + '</div>')
page("hallazgos1", "Calidad · hallazgos 1 a 6", "Doce hallazgos, cada uno con su tratamiento", hcards(H1),
 "Los problemas de unicidad, exactitud y validez están en 2022-2025. Las 60.064 filas de 2026 no tienen duplicados, negativos ni nulos. Solo H5 persiste en 2026.")
page("hallazgos2", "Calidad · hallazgos 7 a 12", "Doce hallazgos, cada uno con su tratamiento (cont.)", hcards(H2),
 "Además, dos problemas ya se resolvieron al normalizar: 11 variantes de categoría para 7 reales, y 8 fechas con hora que el TP1 había descartado.")
page("criterios", "Calidad · decisiones", "Por qué tratamos cada problema así",
 table(["Problema", "Qué hicimos", "Por qué"], [
  ["Claves duplicadas", "Conservar la 1ra ocurrencia", "Con cualquier otro criterio los totales no cierran"],
  ["Stock negativo", "Llevar a 0", "Error de sincronización confirmado (P14-P16)"],
  ["Venta negativa", "Netear con la venta del mes", "Son devoluciones reales, no ritmo de venta (P23)"],
  ["Descuentos > 100% o < 0%", "Excluir del margen", "Error de carga, sin acción comercial detrás (P24-P28)"],
  ["Presupuesto en 0 o negativo", "Excluir del desvío", "Proceso inmaduro en 2022 y error de carga (P29-P32)"],
  ["Historial de precios", "No usarlo", "Es una reconstrucción, no un registro (P9-P10)"],
  ["Comparar entre años", "En unidades, sin deflactar", "La venta ya está a precio actual: IPC corregiría dos veces"],
  ["22 SKUs sin costo", "Costo de OC × 1,2321", "Supuesto sugerido por el negocio y declarado (P3-P7)"]], [26, 30, 44]),
 "Casi todo sigue el default que propuso el negocio en la ronda 2. La única excepción es P13: sugería deflactar por IPC y no lo hicimos porque la venta ya está valuada al precio actual; lo justificamos por escrito.", gap=32)
page("supuesto", "Calidad · supuesto declarado", "El costo de 22 SKUs es un supuesto, y lo decimos",
 '<div style="display:flex; gap:40px; align-items:stretch">'
 + card("0,4471", "costo de OC / precio de lista en los 22 SKUs sin costo → margen de 55,3%, fuera de rango")
 + card("0,5509", "costo de catálogo / precio de lista en el resto del catálogo → margen de 44,9%")
 + card("× 1,2321", "factor que nivela los dos: el costo de OC se ajusta +23,2%. Con la mediana de OC da 1,2307", f"background:{ALT}; border:none")
 + '</div>'
 + f'<div style="display:flex; gap:40px">' + stat("$58,7 M → $72,3 M", "valor del stock de esos 22 SKUs a ago-26 con el costo ajustado")
 + stat("0,999", "relación OC / catálogo en los otros 766 SKUs: la brecha es propia de estos 22, el ajuste no la explica del todo") + '</div>',
 "El negocio pidió calcular este factor y declararlo como supuesto. Sin ajustar, el capital quedaría subestimado y el margen sobreestimado. Queda marcado en el dataset para excluirlo o reemplazarlo cuando Finanzas confirme el costo.")
page("antesdespues", "Calidad · antes y después", "Corregir cambia poco los totales y mucho el detalle",
 chart(IMG["ad"], "Cuatro métricas antes y después de corregir: venta total, capital, participación de Decoración y prevalencia del target",
  stat("< 2%", "cambian venta, unidades y capital al corregir")
  + stat("+1,5 pp", "gana Decoración al unificar categorías: es la candidata al piloto")
  + stat("2,6% → 3,4%", "prevalencia del target al netear las devoluciones en vez de llevarlas a 0 (P23): +30% de positivos, el mayor impacto para el modelo"), 1100, 440),
 "Mensaje: que el total cierre no prueba que los datos estén bien. Los errores se compensan en el agregado (duplicados suman, SKUs sin costo restan) y aparecen al bajar a SKU o categoría.")

# ================================================================= 4 TARGET
divider("d-target", "PARTE 3", "La variable objetivo", "Qué predecimos, por qué esa definición y qué tan firme es cada decisión detrás.", "Variable objetivo: definición, alternativas y solidez")
add("pregunta", f'''<section id="pregunta" data-transition="fade" style="background:{ALT}; color:{INK}; {BF}; padding:128px; display:flex; flex-direction:column; justify-content:center; gap:40px">
<p style="font-size:28px; font-weight:600; letter-spacing:2px; color:{BLUE}">LA PREGUNTA QUE RESPONDE EL MODELO</p>
<h1 style="{HF}; font-size:84px; font-weight:700; line-height:1.1; width:1600px">¿Esta posición SKU–tienda va a tener más de 12 meses de stock dentro de 3 meses?</h1>
<div style="display:flex; gap:24px; flex-wrap:wrap">
<p style="font-size:28px; background:#FFFFFF; border:1px solid {LINE}; border-radius:999px; padding:12px 28px">Binaria: 1 = sí</p>
<p style="font-size:28px; background:#FFFFFF; border:1px solid {LINE}; border-radius:999px; padding:12px 28px">Cobertura = stock / promedio de 12 meses de unidades netas</p>
<p style="font-size:28px; background:#FFFFFF; border:1px solid {LINE}; border-radius:999px; padding:12px 28px">Sin SKUs discontinuados</p></div>
<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:24px">
''' + "".join(f'<div style="display:flex; flex-direction:column; gap:8px; border-left:6px solid {GOLD}; padding:4px 0 4px 24px">'
              f'<p style="{HF}; font-size:32px; font-weight:700; line-height:1.15">{t}</p><p style="font-size:24px; line-height:1.4; color:{BODY}">{b}</p></div>'
              for t, b in [("¿Por qué 3 meses?", "Liquidar o transferir tarda de 2 a 4 semanas. Lo confirmó el negocio."),
                           ("¿Por qué 12 meses?", "Rota menos de una vez al año y deja 420-700 alertas por mes, lo que Operaciones puede atender."),
                           ("Métrica: recall", "Para el negocio, no ver un caso cuesta más que revisar uno de más.")]) + f'''</div>
<p style="position:absolute; left:128px; bottom:64px; width:1664px; font-size:24px; color:{MUT}">Casa Óga · Entregable 2 · Grupo 1 &#160;·&#160; {len(slides)+1}</p>
<aside>Una pregunta que un responsable de Compras entiende sin fórmulas. Los 12 meses salieron primero de la capacidad operativa; que coincida con rotación anual menor a 1 (non-moving en el análisis FSN) se encontró después y sirve de respaldo. Los discontinuados van a una lista aparte con regla fija: ya son una decisión tomada, no algo a predecir.</aside></section>''')
page("ficha", "Target · definición", "Seis decisiones definen el target",
 '<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:24px; flex:1">'
 + card("Unidad: SKU–tienda–mes", "Es donde se decide: liquidar, transferir o frenar la reposición de un producto en una tienda.")
 + card("Universo", "Posiciones con stock en t, no discontinuadas, con al menos 3 meses de historia y observadas en t+3. Con 12 meses se perdían los productos nuevos.")
 + card("Horizonte: 3 meses", "Confirmado por el negocio: menos se confunde con ruido; la acción tarda de 2 a 4 semanas.")
 + card("Umbral: 12 meses", "Rotación anual < 1 (non-moving en el análisis FSN) y compatible con 420-700 intervenciones por mes.")
 + card(f"Prevalencia: {n(RS['prevalencia'],2)}%", f"{n(RS['positivos'],0)} positivos en {n(RS['filas'],0)} filas. {n(RS['tasa_hasta_2025'])}% hasta 2025, {n(RS['tasa_2026'],0)}% en 2026.")
 + card("Métrica: recall", "El negocio declaró más costoso no ver un caso (falso negativo) que revisar uno de más.")
 + '</div>', "Cada decisión tiene un origen: relevamiento con el negocio o medición nuestra. La siguiente diapositiva muestra por qué descartamos las alternativas.", gap=32)
page("candidatos", "Target · alternativas", "Por qué este target y no otro",
 table(["Candidato", "Positivos", "Casos nuevos", "Recall de «sigue igual»", "Veredicto"], [
  ["Dead stock binario (3 condiciones OR)", "8,32%", "62%", "38,4%", "Mezcla criterios; arrastra el ruido de «sin venta»"],
  ["Cobertura > 12 o discontinuado", "3,99%", "67%", "33,5%", "No hay discontinuados en 2026"],
  ["Sin ventas en 3 meses", "6,18%", "65%", "35,3%", "Criterio de consumo masivo; 22% por azar"],
  ["<b>Cobertura > 12, sin discontinuados</b>", "<b>3,40%</b>", "<b>61%</b>", "<b>38,6%</b>", "<b>Elegido</b>"],
  ["Cobertura > 9 (rojo + amarillo)", "9,93%", "62%", "38,5%", "Alternativa si falta volumen"]], [34, 13, 15, 19, 19], 26)
 + f'<p style="font-size:24px; line-height:1.45; color:{BODY}; width:1664px"><b>Cómo leerlo:</b> «sigue igual» es una regla que dice «la posición va a estar como está hoy»; «casos nuevos» son los que esa regla no ve: 6 de cada 10 positivos hoy todavía no lo son, y ahí aporta el modelo. Como los cinco quedan entre 34% y 39%, elegimos por negocio: umbral relativo a la rotación de cada SKU (lo pidió Comercial), sin discontinuados (en 2026 no hay) y un evento sobre el que se puede actuar.</p>',
 f"Comparamos cinco candidatos sobre las mismas {n(RS['filas'],0)} filas. Con 12 meses de historia el elegido era además el menos inercial (32,5% contra 42%); al incluir productos nuevos esa ventaja desaparece y lo decimos. El catálogo está congelado desde junio de 2025: en 2026 no hay discontinuados. María G. es la aprobadora formal del target: la cátedra pide validarlo antes de etiquetar.", gap=24)
page("solidez", "Target · solidez", "Qué tan firme es cada decisión, dicho con honestidad",
 table(["Decisión", "En qué se apoya", "Solidez"], [
  ["Cobertura como métrica", "El negocio pidió un umbral relativo a la rotación de cada SKU", "Firme"],
  ["Horizonte de 3 meses", "Confirmado por el negocio", "Firme"],
  ["Priorizar recall", "El negocio declaró el falso negativo como más costoso", "Firme"],
  ["Corte en 12 meses", "Capacidad operativa + rotación anual < 1 (FSN)", "Media"],
  ["Devoluciones neteadas", "Default del negocio (P23)", "Media"],
  ["Corte amarillo en 9 meses", "Solo el percentil 90 de nuestra distribución", "Débil"],
  ["Acciones por banda", "Asignación nuestra, sin respaldo externo", "Débil"]], [30, 55, 15], 26)
 + f'<p style="font-size:26px; line-height:1.45; color:{BODY}; width:1600px"><b>Pendiente de aprobación de María G. (Comercial).</b> Le pedimos cambiar el semáforo 30/70 que ya había aprobado: marca en rojo al 74% del catálogo contra una capacidad de 420-700 intervenciones por mes.</p>',
 "No existe un umbral académico de cobertura para hogar y decoración: cada retailer lo calibra. Lo decimos así en vez de aparentar un estándar. Las débiles se validan con el negocio.", gap=32)
page("prevalencia", "Target · estabilidad", "La prevalencia salta en 2026: la partición tiene que ser temporal",
 chart(IMG["prev"], "Porcentaje de positivos por mes de corte, coloreado por bloque de la partición",
  "".join(stat(nm, f"{fm(SP_[k]['desde'])} a {fm(SP_[k]['hasta'])} · {n(SP_[k]['positivos'],0)} positivos en {n(SP_[k]['filas'],0)} filas") for nm, k in
          [(f"Train · {n(SP_['train']['tasa'],2)}%", "train"), (f"Validación · {n(SP_['validacion']['tasa'],2)}%", "validacion"), (f"Test · {n(SP_['test']['tasa'],2)}%", "test")])
  .replace("font-size:52px", "font-size:40px")
  + f'<p style="font-size:22px; line-height:1.4; color:{MUT}">Entre bloques, 3 meses de embargo (igual al horizonte): ninguna etiqueta de train cae en el período de validación.</p>'
  + f'<p style="font-size:22px; line-height:1.4; color:{INK}"><b>Clases desbalanceadas ({n(RS["prevalencia"],1)}% positivos):</b> se prioriza recall y el umbral del modelo se elige en validación según las 420-700 alertas por mes.</p>', 1000, 466).replace("gap:28px", "gap:20px", 1),
 "Una partición aleatoria mezclaría meses y el modelo vería el futuro. El test en 2026 mide si el modelo resiste un cambio de régimen: es la prueba más exigente posible; sus métricas no se comparan con las de validación como si fueran el mismo problema. "
 "Con 3,4% de positivos, un modelo que diga siempre «no» acierta el 96,6% y no sirve: por eso no se mira exactitud sino recall dentro de la capacidad de alertas.")

# ================================================================= 5 DATASET
divider("d-data", "PARTE 4", "El dataset de entrenamiento", "Qué información ve el modelo, qué variables entran, cuáles no y por qué.", "Dataset de entrenamiento: variables, exclusiones, leakage y transformaciones")
page("ficha-ds", "Dataset · ficha", f"dataset_entrenamiento_{RS['version']}",
 '<div style="display:flex; gap:48px">' + stat(n(RS["filas"],0), "filas SKU–tienda–mes") + stat(str(RS["n_num"]+RS["n_cat"]), f"features: {RS['n_num']} numéricas y {RS['n_cat']} categóricas")
 + stat(n(RS["positivos"],0), f"positivos ({n(RS['prevalencia'],2)}%)") + stat(n(RS["posiciones"],0), f"posiciones · {RS['skus']} SKUs · 28 tiendas") + '</div>'
 + f'<div style="background:{ALT}; border-radius:16px; padding:36px 40px; display:flex; flex-direction:column; gap:14px">'
 f'<h3 style="{HF}; font-size:34px; font-weight:700">11 de las 15 fuentes, unidas en un panel mensual</h3>'
 f'<p style="font-size:26px; line-height:1.5; color:{BODY}">Ventas ⋈ Stock por (mes, tienda, SKU) es la base. Se suman catálogo y proveedores por SKU; tiendas por tienda; depósito y OC por (mes, SKU); '
 'transferencias y liquidaciones por (mes, tienda, SKU); promociones por (mes, categoría); presupuesto por (mes, tienda, categoría). '
 'Ninguna fuente tiene datos personales: no aplica anonimización (Ley 25.326).</p>'
 f'<p style="font-size:24px; color:{MUT}">Se genera con Modelo/construir_dataset_modelo.py desde Datasets_Normalizados: reproducible de punta a punta.</p></div>',
 "v3: el universo pasa de 12 a 3 meses de historia (entran los productos nuevos) y salen precio, costo y margen del catálogo (son el valor de hoy) y el stock en tránsito (H6). La selección fina de variables se hace en el modelado.")
tl = (f'<div style="position:relative; width:1664px; height:560px">'
      f'<div style="position:absolute; left:0; top:40px; width:1060px; height:300px; background:#E3ECF7; border-radius:16px"></div>'
      f'<p style="position:absolute; left:32px; top:64px; width:1000px; font-size:30px; font-weight:700; color:{INK}">Historia hasta el cierre del mes t: se puede usar</p>'
      f'<p style="position:absolute; left:32px; top:120px; width:1000px; font-size:26px; line-height:1.45; color:{BODY}">Ventas y stock de los últimos 12 meses · OC recibidas y OC pedidas que siguen pendientes · transferencias y liquidaciones ya ocurridas · promociones vigentes · presupuesto cumplido · catálogo con fecha de baja ≤ t</p>'
      f'<div style="position:absolute; left:1090px; top:0px; width:8px; height:420px; background:{GOLD}"></div>'
      f'<p style="position:absolute; left:1000px; top:430px; width:190px; font-size:28px; font-weight:700; text-align:center; color:{INK}">t</p>'
      f'<div style="position:absolute; left:1130px; top:40px; width:534px; height:300px; background:#FBE3D6; border-radius:16px"></div>'
      f'<p style="position:absolute; left:1160px; top:64px; width:480px; font-size:30px; font-weight:700; color:{INK}">t+1 a t+3: no se puede</p>'
      f'<p style="position:absolute; left:1160px; top:120px; width:480px; font-size:26px; line-height:1.45; color:{BODY}">Venta, stock, liquidaciones, transferencias y presupuesto futuros. Solo se mira el calendario comercial fijo (Hot Sale, Black Friday, Navidad).</p>'
      f'<p style="position:absolute; left:1130px; top:370px; width:534px; font-size:28px; font-weight:700; color:{ORANGE}">t+3: se mide la etiqueta</p>'
      f'<p style="position:absolute; left:0; top:480px; width:1060px; font-size:26px; line-height:1.4; color:{BODY}">Además: transformaciones ajustadas solo con train, embargo de 3 meses entre bloques y discontinuados fuera del universo.</p></div>')
page("leakage", "Dataset · data leakage", "Qué información ve el modelo al predecir", tl,
 "La regla central: al predecir en el mes t solo se usa lo que Casa Óga conoce al cierre de t. Los eventos de calendario son la excepción justificada porque son fijos y se conocen con años de anticipación.")
GR = [("Demanda e historia · 14", "Unidades de t, t-1, t-2, 3, 6 y 12 meses, máximo, variabilidad, tendencia, meses con y sin venta, antigüedad de la posición e indicador de historia corta.", "Es donde está la señal: la rotación de la posición."),
      ("Stock · 5", "Disponible, variación a 3 meses, cobertura actual y de hace 3 meses, cambio de cobertura.", "La trayectoria anticipa el cruce del umbral."),
      ("SKU en la cadena · 8", "Stock y cobertura del SKU en las 28 tiendas y en depósito, tiendas en rojo, tendencia del SKU.", "El problema es de producto y de compra, no de tienda."),
      ("Contexto de tienda · 6", "Tendencia de la tienda y de la categoría, peso de la posición, % de posiciones en rojo, cumplimiento presupuestario.", "Separa un problema del producto de uno de la tienda."),
      ("Abastecimiento · 10", "OC recibidas y pendientes, meses desde la última OC, transferencias recibidas y enviadas, lead time y pedido mínimo.", "Lo que entra es lo que genera el sobrestock."),
      ("Acciones comerciales · 7", "Liquidación activa y su descuento, liquidaciones de la posición y del SKU, promociones de la categoría.", "Registran lo que ya se hizo sobre la posición."),
      ("Producto · 5", "Precio relativo a la subcategoría, antigüedad del SKU; categoría, subcategoría, proveedor.", "Contexto y palanca de Compras (proveedor)."),
      ("Tienda y calendario · 5", "m², región, formato; mes del año y eventos fijos en el horizonte.", "Segmentación y estacionalidad, que el modelo verifica.")]
page("grupos", "Dataset · variables elegidas", f"{RS['n_num']+RS['n_cat']} variables en 8 grupos, cada uno con su porqué",
 '<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:20px; flex:1">' + "".join(
  f'<div style="display:flex; flex-direction:column; gap:10px; background:#FFFFFF; border:1px solid {LINE}; border-radius:12px; padding:24px">'
  f'<h3 style="{HF}; font-size:28px; font-weight:700; line-height:1.15; color:{BLUE}">{t}</h3><p style="font-size:24px; line-height:1.35; color:{BODY}">{d}</p>'
  f'<p style="font-size:24px; line-height:1.35; color:{INK}"><b>{w}</b></p></div>' for t, d, w in GR) + '</div>',
 "El detalle de cada variable está en diccionario_features_v2.csv. Todas tienen fundamento de negocio; ninguna se eligió mirando el test.", gap=28)
def lista(t, color, items):
    return (f'<div style="flex:1; display:flex; flex-direction:column; gap:14px; background:#FFFFFF; border:1px solid {LINE}; border-top:6px solid {color}; border-radius:12px; padding:28px">'
            f'<h3 style="{HF}; font-size:32px; font-weight:700">{t}</h3>'
            + "".join(f'<p style="font-size:24px; line-height:1.35; color:{BODY}"><b style="color:{INK}">{a if a.endswith(".") else a + "."}</b> {b}</p>' for a, b in items) + '</div>')
page("excluidas", "Dataset · variables excluidas", "Lo que quedó afuera, y por qué",
 '<div style="display:flex; gap:24px; flex:1">'
 + lista("Leakage", ORANGE, [("Venta y stock de t+1 a t+3", "definen el target"), ("Liquidaciones, transferencias y OC posteriores a t", "son reacciones al sobrestock"),
                             ("Estado del catálogo", "es una foto de hoy: revela bajas futuras"), ("Presupuesto futuro", "se reajusta con la venta real (P31)"),
                             ("Promociones futuras", "no hay evidencia de que se planifiquen con anticipación")])
 + lista("Calidad", BLUE, [("Antigüedad de tienda", "6 tiendas venden antes de abrir (H3)"), ("Precio, costo y margen del catálogo", "son el valor de hoy: anacrónicos para meses pasados"), ("Precio del historial", "reconstrucción retroactiva (H8)"), ("Stock en tránsito", "sin definición y sin señal en 2026 (H6)"),
                           ("Devoluciones por motivo", "no hay datos de 2026 (H12)"), ("Temporada y feriados", "el Calendario no cubre 2026 (H12)")])
 + lista("Generalización y otros", "#6B7280", [("Id de tienda y de SKU", "el modelo memorizaría posiciones"), ("Marca de costo imputado", "constante en train; queda como control"),
                                              ("Costo de almacenamiento", "constante por categoría"), ("Cliente o ticket", "no existe en ninguna fuente")])
 + '</div>', "Cada exclusión tiene motivo escrito en la Parte B. Las de leakage son las más importantes: con cualquiera de ellas el modelo daría resultados excelentes en el papel e inútiles en la práctica.", gap=28)
page("transformaciones", "Dataset · preparación para el modelo", "Transformaciones, todas ajustadas solo con train",
 table(["Transformación", "Qué se hizo", "Por qué"], [
  ["Valores extremos", "Winsorización p1-p99 en 45 continuas", "Colas largas reales, no errores: no se borran filas"],
  ["Distribuciones sesgadas", "log(1+x) en 25 variables", "Reduce el peso de los extremos (cobertura: asimetría 3,98)"],
  ["Escalado", "Estandarización con media y desvío de train", "Escalas muy distintas; lo necesita la regresión logística"],
  ["Categóricas", "One-hot de categoría, subcategoría, región, formato, proveedor", "Son nominales: label encoding inventaría un orden"],
  ["Temporales", "Mes como seno y coseno, ventanas de 3/6/12 meses, antigüedad", "Diciembre queda junto a enero; la trayectoria anticipa"],
  ["Faltantes", "Topes, indicadores y medianas de train", "Son denominadores cero o eventos ausentes, no datos perdidos"],
  ["Balanceo", "Ponderación de clases (≈55), sin SMOTE", "SMOTE mezclaría meses y rompería la estructura temporal"]], [22, 38, 40], 25)
 + f'<p style="font-size:24px; color:{MUT}">Dos versiones: sin transformar para árboles y transformada para una regresión logística, que es la línea base explicable que exige el negocio.</p>',
 "Ningún parámetro de transformación se calcula con validación o test: sería otra forma de leakage.", gap=32)

# ================================================================= 6 SENAL
divider("d-senal", "PARTE 5", "¿El dataset tiene señal?", "Antes de modelar: qué separa a las posiciones que van a caer en rojo, y qué agrega un modelo sobre el semáforo actual.", "Señal del dataset y capital en riesgo")
H = I["mapa_riesgo"]; og = I["origen_positivos"]; mx = max(v for row in H["tasa"] for v in row if v is not None)
def heat(v):
    if v is None: return ("#EEF1F5", MUT, "—")
    t = (v / mx) ** .5
    c0, c1 = (0xEE, 0xF3, 0xFA), (0x1F, 0x4E, 0x8C)
    rgb = "#" + "".join(f"{round(a + (b - a) * t):02X}" for a, b in zip(c0, c1))
    return (rgb, "#FBFBF8" if t > .55 else INK, n(v) + "%")
hc = f'<p style="font-size:24px; color:{MUT}; padding:6px"></p>' + "".join(f'<p style="font-size:24px; font-weight:700; color:{MUT}; padding:6px; text-align:center">{t}</p>' for t in H["tend"])
for i in range(len(H["cob"]) - 1, -1, -1):
    hc += f'<p style="font-size:24px; color:{BODY}; padding:6px; text-align:right">{H["cob"][i]} meses</p>'
    for v in H["tasa"][i]:
        bgc, fg, t = heat(v); hc += f'<p style="font-size:28px; font-weight:700; color:{fg}; background:{bgc}; padding:14px 6px; border-radius:8px; text-align:center">{t}</p>'
page("mapariesgo", "Señal · cobertura × tendencia", "La tendencia multiplica el riesgo",
 '<div style="display:flex; gap:56px; flex:1">'
 f'<div style="display:flex; flex-direction:column; gap:12px"><div style="display:grid; grid-template-columns:200px repeat(4, 220px); gap:8px">{hc}</div>'
 f'<p style="font-size:24px; color:{MUT}">% que cae en rojo 3 meses después. Filas: cobertura hoy. Columnas: venta de 3 meses vs promedio de 12.</p></div>'
 '<div style="flex:1; display:flex; flex-direction:column; gap:28px">'
 + stat(f"{n(H['tasa'][3][2])}% → {n(H['tasa'][3][0])}%", "riesgo con 9-12 meses de cobertura si la venta está estable o si cae más de 50%")
 + stat(f"{n(sum(og['pct'][:3]),0)}%", "de los casos hoy no está en rojo: un semáforo sobre el presente no los ve") + '</div></div>',
 "Ninguna regla de un solo umbral combina cobertura y tendencia. Esto justifica un modelo multivariado y, a la vez, confirma que las variables elegidas tienen señal.")
cpv = I["capacidad"]["validacion"]; k4, k7 = cpv["k"].index(420), cpv["k"].index(700)
import csv
cpt = {int(r["alertas_mes"]): r for r in csv.DictReader(open(os.path.join(E2, "Modelo", "resultados", "capacidad_alertas_v3.csv"), encoding="utf-8")) if r["split"] == "test"}
t4, t7 = cpt[420], cpt[700]
page("capacidad", "Señal · capacidad operativa", "El modelo encuentra más casos en 2025; en 2026 la ventaja se achica",
 chart(IMG["cap"], "Porcentaje de casos capturados según alertas por mes, modelo de prueba contra regla de cobertura actual, en validación y en test",
  stat(f"{n(cpv['recall_modelo'][k4],0)}% vs {n(cpv['recall_regla'][k4],0)}%", "casos capturados con 420 alertas por mes en validación (2025): modelo contra ordenar por cobertura actual")
  + stat(f"{n(float(t4['recall_modelo']),0)}% vs {n(float(t4['recall_regla']),0)}%", f"en test (2026) con 420 alertas: la regla casi lo alcanza. Con 700: {n(float(t7['recall_modelo']),0)}% vs {n(float(t7['recall_regla']),0)}%")
  + f'<p style="font-size:24px; line-height:1.4; color:{MUT}">Con 420 alertas acierta 1 de cada 5 en 2025 (precisión {n(cpv["precision_modelo"][k4],0)}%). En 2026 hay {t4["positivos_mes"]} casos por mes: más que la capacidad. Modelo de prueba sin ajustar, no el final.</p>'),
 "La franja amarilla es la capacidad declarada de 15 a 25 intervenciones por tienda, que nunca se midió. En 2026 la regla simple se acerca: el modelo final tiene que ganar ahí, y los casos superan la capacidad. Hay que validarla con Lucía O.")
page("senal", "Señal · por variable", "La señal está en la demanda de la posición",
 chart(IMG["senal"], "AUC de cada una de las 15 variables con más señal, en train y en test",
  stat(f"{I['senal_sin']} de {I['n_features_num']}", "variables numéricas no separan solas (AUC < 0,55): liquidaciones, promociones, OC y transferencias")
  + stat("0,61 → 0,50", "AUC de la antigüedad de la posición de train a test: en 2026 no hay productos nuevos (catálogo congelado)")
  + f'<p style="font-size:26px; line-height:1.4; color:{BODY}">Se mantienen todas: pueden aportar en combinación. La selección se hace en el modelado.</p>', 900, 637),
 "AUC 0,5 es azar. Que las acciones comerciales no separen solas es coherente: se aplicaron caso por caso y sin protocolo. La antigüedad vuelve a importar cuando haya lanzamientos: por eso queda.")
rc = I["rojo_ago26_cat"]; rs = I["rojo_ago26_sku"]
page("capital", "Contexto · capital en riesgo hoy", "Cuánto capital está en posiciones con más de 12 meses de stock",
 chart(IMG["caprojo"], "Capital a costo en posiciones con más de 12 meses de cobertura por categoría, agosto 2026",
  stat(f"${n(rc['total_cap'])} M", f"a costo en {n(rc['total_pos'],0)} posiciones y {rs['skus']} SKUs, ago-26")
  + stat(f"${n(rc['total_cap']*0.05)} M/mes", "de costo de sostenerlo, al 5% mensual declarado por el negocio")
  + stat(f"{n(rs['top20_pct'])}%", "del capital en rojo está en 20 SKUs: el problema es de producto"), 1000, 569),
 "Todas las categorías tienen entre 4,7% y 7,5% de su stock en rojo: no es un problema de una categoría. Los SKUs más cargados están en rojo en 1 a 3 tiendas: ahí la acción es transferir.")

# ================================================================= 7 CIERRE
page("limites", "Cierre", "Limitaciones que declaramos y lo que queda pendiente",
 '<div style="display:flex; gap:32px; flex:1">'
 + lista("Limitaciones", ORANGE, [("2026 sin devoluciones", "el neteo es asimétrico entre años (H12)"), ("Precio y costo", "el catálogo guarda solo el valor actual: se usa solo el precio relativo"), ("Posiciones con < 3 meses", "fuera del modelo: requieren una regla aparte"),
                                  ("Venta antes de abrir", "6 tiendas sin explicación (H3)"), ("Capacidad de 15-25 por tienda", "nunca se midió"),
                                  ("Costo de 22 SKUs", "supuesto, no dato")])
 + lista("Pendientes", BLUE, [("María G.", "aprobar target, cortes y acciones por banda"), ("Lucía O.", "confirmar la capacidad operativa"),
                              ("Negocio", "responder H3, H6 y H12; extender Devoluciones, Calendario y catálogo a 2026"),
                              ("Equipo", "decidir si el motivo «sin rotación» (devolución a proveedor) se netea")])
 + '</div>', "Ninguna de estas limitaciones bloquea el modelado, pero todas se declaran en el entregable.", gap=32)
add("proximo", f'''<section id="proximo" style="background:{DARK}; color:{LIGHT}; {BF}; padding:128px; display:flex; flex-direction:column; justify-content:center; gap:36px">
<div style="width:120px; height:8px; background:{GOLD}"></div>
<p style="font-size:28px; font-weight:600; letter-spacing:2px; color:{GOLD}">PRÓXIMO PASO · ENTREGABLE 3</p>
<h1 style="{HF}; font-size:88px; font-weight:700; line-height:1.08; width:1500px; color:{LIGHT}">Modelar sobre un dataset que ya sabemos que tiene señal</h1>
<div style="display:flex; gap:32px">
<p style="flex:1; font-size:30px; line-height:1.4; color:#C9D2E3">Regresión logística como línea base explicable y gradient boosting como alternativa.</p>
<p style="flex:1; font-size:30px; line-height:1.4; color:#C9D2E3">Umbral elegido por capacidad operativa, no por un corte de probabilidad.</p>
<p style="flex:1; font-size:30px; line-height:1.4; color:#C9D2E3">Evaluación en 2026 para medir robustez ante el cambio de régimen.</p></div>
<aside>Cerramos con el puente al próximo entregable. El dataset, los scripts y el dashboard están en el repo del grupo.</aside></section>''')

# ---------------------------------------------------------------- escribir
for sid, html in slides:
    open(os.path.join(OUT, "slides", f"{sid}.html"), "w", encoding="utf-8").write(html)
idx = {"v": 4, "createdOnFiles": {"v": 1, "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
       "title": "Casa Óga · Entregable 2", "order": [s for s, _ in slides], "sections": sections, "cover": "portada",
       "faces": {"dm-sans": {"family": "DM Sans", "href": "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400..700&display=swap"},
                 "ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap"}},
       "designSystems": []}
json.dump(idx, open(os.path.join(OUT, "deck.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(slides), "slides:", ", ".join(s for s, _ in slides))
