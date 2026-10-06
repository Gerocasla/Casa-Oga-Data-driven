# -*- coding: utf-8 -*-
"""
Consolida el Entregable 2 (Parte A + Parte B) en un solo documento Word.

Entrada : ../Entregable 2 - Parte A - COMPLETADO.docx · ../Entregable 2 - Parte B - COMPLETADO.docx
          (mismos estilos, numeracion y configuracion: se fusiona el XML directamente)
Salida  : ../Entregable 2 - Consolidado - Grupo 1.docx  y  1-Entregable-2-Consolidado.docx (copia para el envio)

Ademas de unir, aplica la revision del consolidado (cada cambio con su motivo en REVISION).
"""
import os, re, sys, copy, shutil, zipfile
from lxml import etree

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
E2 = os.path.dirname(BASE)
SRC_A = os.path.join(E2, "Entregable 2 - Parte A - COMPLETADO.docx")
SRC_B = os.path.join(E2, "Entregable 2 - Parte B - COMPLETADO.docx")
OUT = os.path.join(E2, "Entregable 2 - Consolidado - Grupo 1.docx")
OUT_ENVIO = os.path.join(BASE, "1-Entregable-2-Consolidado.docx")

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
      "pr": "http://schemas.openxmlformats.org/package/2006/relationships"}
W = "{%s}" % NS["w"]

za, zb = zipfile.ZipFile(SRC_A), zipfile.ZipFile(SRC_B)
docA = etree.fromstring(za.read("word/document.xml"))
docB = etree.fromstring(zb.read("word/document.xml"))
# el merge directo solo es valido si las dos partes comparten plantilla (estilos y numeracion)
assert za.read("word/styles.xml") == zb.read("word/styles.xml") and za.read("word/numbering.xml") == zb.read("word/numbering.xml")
bodyA, bodyB = docA.find(W + "body"), docB.find(W + "body")
A, B = list(bodyA), list(bodyB)
sect = A[-1]
assert sect.tag == W + "sectPr"

def texto(el): return "".join(el.itertext())
def idx(lista, empieza):
    hits = [i for i, e in enumerate(lista) if texto(e).startswith(empieza)]
    assert len(hits) == 1, (empieza, hits); return hits[0]

# ------------------------------------------------------------------ revision: reemplazos de texto (cada uno debe existir una sola vez)
REVISION = [
 # caratula
 (A, "Entregable Nro 2", "Entregable Nro 2 — Documento consolidado (Partes A y B)", "Carátula del consolidado"),
 (A, "Entregable 2 · Parte A: Alcance, Analítica Descriptiva y Evaluación de Calidad de Datos",
     "Parte A: Alcance, Analítica Descriptiva y Evaluación de Calidad de Datos · Parte B: Corrección de Datos y Preparación de Datos para el Modelo", "Carátula"),
 (A, "Simón Volpato Escandarani — [legajo]", "Simón Volpato Escandarani — 64784", "Legajo (Entregable 1 consolidado)"),
 (A, "Dashboard y visualización", "", "Roles: se dejan vacíos"),
 (A, "__/__/2026", "06/10/2026", "Fecha de entrega"),
 (A, "v1.0", "v2.0 — consolidado", "Versión"),
 # Parte A
 (A, "(a dic-2025 era de 20 veces)", "(a dic-2025 era de 27 veces: 23.528 contra 868)",
     "Reconciliado con §3.1, que da 23.528 contra 868 (EDA/resultados/eda_chequeos_2_log.txt)"),
 (A, "El cumplimiento se mantiene entre 90% y 92% en todos los niveles de apertura (año, categoría, tienda y celda individual)",
     "El cumplimiento se mantiene entre 89% y 92% en todos los niveles de apertura (año, categoría y tienda; la mediana por celda es 90,5%)",
     "Reconciliado con §2.3 (89,3% a 91,4% por año, categoría y tienda)"),
 (A, "La columna de referencia indica el gráfico del Anexo que acompaña cada fila.",
     "La columna de referencia indica el gráfico del Anexo A que acompaña cada fila.", "Anexo renombrado"),
 (A, "Anexo · Gráficos del análisis descriptivo", "Anexo A · Gráficos del análisis descriptivo (Parte A)", "Anexo al final del consolidado"),
 # Parte B
 (B, "Es el único hallazgo de consistencia que persiste en 2026.", "Persiste en 2026 (187 y 449 filas), igual que H6.",
     "H6 también persiste en 2026 (8.771 vs 936 a ago-26)"),
 (B, "condicionan la confiabilidad de las métricas centrales del proyecto y deberían resolverse antes de construir el dataset de entrenamiento.",
     "condicionan la confiabilidad de las métricas centrales del proyecto: para construir el dataset de entrenamiento se aplicaron las remediaciones del pipeline descritas en cada fila, y la corrección en origen debería completarse antes de poner el modelo en producción.",
     "El dataset ya está construido con las remediaciones del pipeline (§2)"),
 (B, "El dashboard (Dashboard-Calidad-Antes-Despues.html, generado por EDA/antes_despues.py) calcula cada métrica dos veces.",
     "Cada métrica se calcula dos veces (EDA/antes_despues.py); el dashboard que acompaña esta entrega (5-Dashboard-Antes-vs-Despues.html) resume el resultado con las mismas cifras y criterios de la presentación.",
     "Referencia al archivo que efectivamente se entrega"),
 (B, "• Tienda (1 + 2 categóricas): m² de venta; región y formato.  • Temporal (2): mes del año y meses con evento comercial fijo entre t+1 y t+3.",
     "• Tienda y calendario (3 + 2 categóricas): m² de venta, mes del año y meses con evento comercial fijo entre t+1 y t+3; región y formato.",
     "Mismos 8 grupos que la presentación y el diccionario"),
 (B, "Generado por Modelo/construir_dataset_modelo.py, reproducible desde Datasets_Normalizados.",
     "Generado por Modelo/construir_dataset_modelo.py, reproducible desde Datasets_Normalizados. Se entrega en CSV (3-Dataset-Modelo-v3.zip) junto con el diccionario de datos completo (4-Diccionario-de-Datos-v3.xlsx).",
     "Archivos entregados"),
 (B, "Colas largas: la cobertura tiene percentil 99 de 15 meses y máximo de 84.",
     "Colas largas: en train, la cobertura tiene percentil 99 de 18 meses y máximo de 128.",
     "Valores de la v3 (Modelo/resultados/construir_dataset_log.txt)"),
 (B, "(la cobertura tenía asimetría 3,98)", "(la cobertura tenía asimetría 5,09 en train)", "Valor de la v3 (mismo log)"),
 (B, "Las escalas son muy distintas (precios en decenas de miles, conteos de 0 a 12).",
     "Las escalas son muy distintas (stock de la cadena en miles de unidades, proporciones entre 0 y 1, conteos de 0 a 12).",
     "En la v3 el precio absoluto ya no es variable"),
]
def reemplazar(elementos, viejo, nuevo):
    hits = []
    for el in elementos:
        for t in el.iter(W + "t"):
            if t.text and viejo in t.text: hits.append(t)
    assert len(hits) == 1, (viejo, len(hits))
    hits[0].text = hits[0].text.replace(viejo, nuevo)
for lista, viejo, nuevo, _ in REVISION:
    reemplazar(lista, viejo, nuevo)

# ------------------------------------------------------------------ piezas nuevas (mismo formato que el resto del documento)
def run(txt, sz=21, b=False, color=None, i=False):
    r = etree.SubElement(etree.Element(W + "dummy"), W + "r")
    rpr = etree.SubElement(r, W + "rPr")
    if b: etree.SubElement(rpr, W + "b"); etree.SubElement(rpr, W + "bCs")
    if i: etree.SubElement(rpr, W + "i"); etree.SubElement(rpr, W + "iCs")
    if color: etree.SubElement(rpr, W + "color").set(W + "val", color)
    etree.SubElement(rpr, W + "sz").set(W + "val", str(sz)); etree.SubElement(rpr, W + "szCs").set(W + "val", str(sz))
    t = etree.SubElement(r, W + "t"); t.text = txt; t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r
def par(runs, before=0, after=110, jc="both", line=276, estilo=None, shd=None, salto_antes=False):
    p = etree.Element(W + "p"); ppr = etree.SubElement(p, W + "pPr")
    if estilo: etree.SubElement(ppr, W + "pStyle").set(W + "val", estilo)
    if salto_antes: etree.SubElement(ppr, W + "pageBreakBefore")
    if shd:
        s = etree.SubElement(ppr, W + "shd"); s.set(W + "fill", shd); s.set(W + "color", "auto"); s.set(W + "val", "clear")
    sp = etree.SubElement(ppr, W + "spacing"); sp.set(W + "before", str(before)); sp.set(W + "after", str(after)); sp.set(W + "line", str(line))
    etree.SubElement(ppr, W + "jc").set(W + "val", jc)
    for r in runs: p.append(r)
    return p
def salto():
    p = etree.Element(W + "p"); r = etree.SubElement(p, W + "r"); etree.SubElement(r, W + "br").set(W + "type", "page"); return p
def titulo_seccion(txt):   # Heading 1 con el formato del documento
    return par([run(txt, 28, b=True)], 300, 150, "left", 276, "Heading1", "F2F2F2")
def subtitulo(txt): return par([run(txt, 21, b=True)], 180, 70, "left")
def divisor(parte, nombre, resumen):
    return [par([run(parte.upper(), 20, color="808080")], 2400, 60, "center", 276, salto_antes=True),
            par([run(nombre, 38, b=True)], 0, 200, "center"),
            par([run(resumen, 21, color="595959")], 0, 110, "center")]

def tabla(plantilla, filas):
    """Copia una tabla del documento (encabezado + 1ra fila de datos como molde) y la llena con 'filas'."""
    t = copy.deepcopy(plantilla)
    trs = t.findall(W + "tr"); enc, molde = trs[0], trs[1]
    for tr in trs[1:]: t.remove(tr)
    def llenar(tr, valores):
        for tc, v in zip(tr.findall(W + "tc"), valores):
            ps = tc.findall(W + "p")
            for p in ps[1:]: tc.remove(p)
            rs = ps[0].findall(W + "r")
            for r in rs[1:]: ps[0].remove(r)
            ts = rs[0].findall(W + "t")
            for x in ts[1:]: rs[0].remove(x)
            ts[0].text = v
    llenar(enc, filas[0])
    for f in filas[1:]:
        tr = copy.deepcopy(molde); llenar(tr, f); t.append(tr)
    return t

plant3 = A[idx(A, "Elemento del informe")]   # tabla de 3 columnas de la Parte A §2.2

nota = [titulo_seccion("Sobre este documento"),
 par([run("Este documento consolida en una sola pieza las dos partes del Entregable 2, con el corte de datos de agosto de 2026. "
          "La Parte A construye el panorama descriptivo de las 15 fuentes y evalúa su calidad en siete dimensiones. "
          "La Parte B define el tratamiento de cada hallazgo, mide su efecto comparando los datos antes y después de la corrección, "
          "y prepara el dataset de entrenamiento del modelo: target, universo, 60 variables, partición temporal y transformaciones.")]),
 par([run("Respecto de las versiones de cada parte, el consolidado unifica la carátula y los anexos, reconcilia cifras que diferían entre secciones "
          "(relación entre stock en tránsito y transferencias a dic-2025, rango del cumplimiento presupuestario, percentiles y asimetría de la cobertura en train), "
          "agrupa las variables en los mismos 8 grupos que la presentación y el diccionario, y referencia los archivos que efectivamente acompañan la entrega.")]),
 subtitulo("Contenido"),
 tabla(plant3, [("Parte / sección", "Contenido", "Resultado principal"),
  ("Parte A · 1 · Introducción y alcance", "Propósito, alcance y definiciones", "15 fuentes, corte ago-2026; unidad de análisis: posición SKU–tienda–mes"),
  ("Parte A · 2 · Analítica descriptiva", "Perfil, estadísticas, evolución, distribución y relaciones (24 métricas)", "La caída de 2026 es sobre todo de surtido; la cola de cobertura se engorda"),
  ("Parte A · 3 · Evaluación de calidad", "Mapa fuente × dimensión y fundamento de cada calificación crítica", "Problemas concentrados en 2022-2025 y en el maestro de producto"),
  ("Parte B · 1 · Hallazgos y plan de mejora", "H1-H12, R1-R2, gaps, mapa actualizado, plan por hallazgo y dashboard antes/después", "Mueven poco los agregados y mucho el target: prevalencia de 2,61% a 3,40%"),
  ("Parte B · 2 · Preparación para el modelo", "Target, universo, fuentes, variables excluidas, partición y transformaciones", "201.306 filas × 60 variables; test 2026 con 9,03% de positivos"),
  ("Anexo A", "Gráficos G1 a G12 del análisis descriptivo", "Referenciados en la Parte A §2.3")]),
 subtitulo("Archivos que acompañan esta entrega"),
 tabla(plant3, [("Archivo", "Contenido", "Dónde se usa"),
  ("2-Presentacion-Final-Entregable-2.html", "Presentación del Entregable 2 en un solo archivo (se abre en el navegador; N muestra las notas)", "Exposición"),
  ("3-Dataset-Modelo-v3.zip", "dataset_entrenamiento_v3.csv: 201.306 filas con el target, las 60 variables, los identificadores, la marca de costo imputado y la partición", "Parte B §2.1"),
  ("4-Diccionario-de-Datos-v3.xlsx", "Diccionario de las 66 columnas (fuente, ventana, unidad, nulos, rango, transformación y señal), grupos, partición, categóricas y variables excluidas", "Parte B §2.1 y §2.2"),
  ("5-Dashboard-Antes-vs-Despues.html", "Resumen de una página: qué corregimos, por qué y cuánto cambian los totales, el detalle por categoría y el target", "Parte B §1.3")])]

# ------------------------------------------------------------------ armado
i_anexo = idx(A, "Anexo A · Gráficos")
assert texto(A[i_anexo - 1]) == "" and A[i_anexo - 1].find(".//" + W + "br") is not None   # salto de pagina previo
caratula, parteA, anexoA = A[0:5], A[5:i_anexo - 1], A[i_anexo:-1]
i_b1 = idx(B, "Sección 1 · Hallazgos")
parteB = B[i_b1:-1]
assert B[-1].tag == W + "sectPr"

nuevo = (caratula + [salto()] + nota
         + divisor("Parte A", "Alcance, Analítica Descriptiva y Evaluación de Calidad de Datos",
                   "Panorama de las 15 fuentes y evaluación de calidad en siete dimensiones") + parteA
         + divisor("Parte B", "Corrección de Datos y Preparación de Datos para el Modelo",
                   "Tratamiento de cada hallazgo, efecto de la corrección y dataset de entrenamiento") + parteB
         + [salto()] + anexoA + [sect])
for e in list(bodyA): bodyA.remove(e)
for e in nuevo: bodyA.append(e)

# ------------------------------------------------------------------ imagenes: la de la Parte B entra con un id nuevo; ids de dibujo unicos
relsA = etree.fromstring(za.read("word/_rels/document.xml.rels"))
relsB = etree.fromstring(zb.read("word/_rels/document.xml.rels"))
usados = {e.get("{%s}embed" % NS["r"]) for e in docA.iter() if e.get("{%s}embed" % NS["r"])}
medios_b = {}
for rel in relsB:
    if rel.get("Type").endswith("/image"):
        nid = "rIdB" + rel.get("Id")[3:]
        destino = "media/parteB_" + os.path.basename(rel.get("Target"))
        medios_b[rel.get("Id")] = (nid, destino, "word/" + rel.get("Target"))
for e in docA.iter():
    v = e.get("{%s}embed" % NS["r"])
    if v and v in medios_b and e in set(parteB_el for x in parteB for parteB_el in x.iter()):
        e.set("{%s}embed" % NS["r"], medios_b[v][0])
usados = {e.get("{%s}embed" % NS["r"]) for e in docA.iter() if e.get("{%s}embed" % NS["r"])}
for rel in list(relsA):   # fuera las imagenes que la Parte A arrastraba sin usar
    if rel.get("Type").endswith("/image") and rel.get("Id") not in usados: relsA.remove(rel)
for vid, (nid, destino, _) in medios_b.items():
    r = etree.SubElement(relsA, "{%s}Relationship" % NS["pr"])
    r.set("Id", nid); r.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"); r.set("Target", destino)
for k, e in enumerate(docA.iter("{%s}docPr" % NS["wp"]), 1): e.set("id", str(k))
assert usados <= {r.get("Id") for r in relsA}

# ------------------------------------------------------------------ escritura
media_ok = {"word/" + r.get("Target") for r in relsA if r.get("Type").endswith("/image")}
tmp = OUT + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in za.infolist():
        n = it.filename
        if n.startswith("word/media/") and n not in media_ok: continue
        data = za.read(n)
        if n == "word/document.xml": data = etree.tostring(docA, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif n == "word/_rels/document.xml.rels": data = etree.tostring(relsA, xml_declaration=True, encoding="UTF-8", standalone=True)
        elif n == "word/header1.xml":
            assert "Entregable 2 · Parte A".encode() in data
            data = data.replace("Entregable 2 · Parte A".encode(), "Entregable 2 · Consolidado (Partes A y B)".encode())
        elif n == "docProps/core.xml":
            data = re.sub(rb"<dc:title>.*?</dc:title>", "<dc:title>Casa Óga · Entregable 2 · Consolidado · Grupo 1</dc:title>".encode(), data)
        zo.writestr(it, data)
    for _, destino, origen in medios_b.values():
        zo.writestr("word/" + destino, zb.read(origen))
os.replace(tmp, OUT)
shutil.copyfile(OUT, OUT_ENVIO)
print("OK:", OUT)
print("Revisión aplicada:")
for _, v, n, m in REVISION: print(f"  - {m}")
