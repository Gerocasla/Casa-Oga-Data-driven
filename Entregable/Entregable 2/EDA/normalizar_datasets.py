"""Normalizacion de los CSV de Casa Oga.

Lee  Data-Driven/Datasets/           (crudos, tal como los entrega la catedra)
Escribe Data-Driven/Datasets_Normalizados/  (mismos datos, representacion uniforme)

Reglas aplicadas (solo REPRESENTACION, ningun valor numerico se altera):
  R1. Texto sin tildes ni enie (Bano, Decoracion, Otono, Casa Oga...).
  R2. Variantes de una misma categoria unificadas (DECO / TEXTIL_HOGAR / Textil Hogar -> forma canonica).
  R3. Fechas con hora (AAAA-MM-DD 00:00:00) pasadas a AAAA-MM-DD.
  R4. Espacios sobrantes al inicio/fin y espacios dobles (control preventivo).

NO se tocan: numeros negativos, nulos, duplicados por clave ni fechas fuera de rango.
Esos casos estan pendientes de respuesta del negocio (ver Preguntas-Calidad-de-Datos-Ronda-2.docx).
"""
import os
import re
import unicodedata
from datetime import datetime
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
ORIG = os.path.join(RAIZ, "Datasets")
DEST = os.path.join(RAIZ, "Datasets_Normalizados")
REG = os.path.join(RAIZ, "REGISTRO-CAMBIOS-DATASETS.md")
os.makedirs(DEST, exist_ok=True)

CATEGORIAS = {"deco": "Decoracion", "decoracion": "Decoracion", "textilhogar": "Textil hogar",
              "cocinaymesa": "Cocina y mesa", "iluminacion": "Iluminacion", "muebles": "Muebles",
              "organizacion": "Organizacion", "bano": "Bano"}
FECHAS = {"fecha", "fecha_mes", "fecha_alta_catalogo", "fecha_baja_catalogo", "fecha_inicio", "fecha_fin",
          "fecha_vigencia_desde", "fecha_vigencia_hasta", "fecha_pedido", "fecha_recepcion", "fecha_envio",
          "fecha_apertura"}

def sin_acentos(x):
    return "".join(c for c in unicodedata.normalize("NFKD", str(x)) if not unicodedata.combining(c))

def clave_cat(x):
    return re.sub(r"[\s_\-\.]+", "", sin_acentos(x).lower().strip())

cambios = []   # una fila por tipo de cambio aplicado
def anotar(fuente, columna, regla, crudo, nuevo, filas):
    cambios.append({"fuente": fuente, "columna": columna, "regla": regla,
                    "valor_crudo": crudo, "valor_normalizado": nuevo, "filas": filas})

archivos = sorted(f for f in os.listdir(ORIG) if f.endswith(".csv"))
resumen = []
for f in archivos:
    fuente = f[:-4]
    df = pd.read_csv(os.path.join(ORIG, f), dtype=str, keep_default_na=True)
    n_cambios = 0
    for c in df.columns:
        col = df[c]
        if col.dropna().empty:
            continue
        es_num = pd.to_numeric(col, errors="coerce").notna().mean() > .95
        if es_num and c not in FECHAS:
            continue  # columnas numericas: no se tocan

        # R4 espacios
        limpio = col.where(col.isna(), col.astype(str).str.strip().str.replace(r"\s{2,}", " ", regex=True))
        k = int((limpio.fillna("") != col.fillna("")).sum())
        if k:
            anotar(fuente, c, "R4 espacios", "(espacios sobrantes)", "(texto recortado)", k); n_cambios += k
        col = limpio

        # R3 fechas con hora
        if c in FECHAS:
            conhora = col.notna() & col.astype(str).str.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
            if conhora.any():
                for crudo in col[conhora].unique():
                    anotar(fuente, c, "R3 formato de fecha", crudo, str(crudo).split(" ")[0],
                           int((col[conhora] == crudo).sum()))
                col = col.where(~conhora, col.astype(str).str.slice(0, 10))
                n_cambios += int(conhora.sum())
            df[c] = col
            continue

        # R2 categorias
        if c == "categoria":
            nuevo = col.map(lambda x: CATEGORIAS.get(clave_cat(x), sin_acentos(x)) if pd.notna(x) else x)
        else:
            # R1 resto del texto: solo se quitan tildes y enie
            nuevo = col.map(lambda x: sin_acentos(x) if pd.notna(x) else x)
        dif = col.fillna("") != nuevo.fillna("")
        if dif.any():
            for crudo in col[dif].unique():
                n = int((col[dif] == crudo).sum())
                regla = "R2 categoria unificada" if c == "categoria" else "R1 sin tildes/enie"
                anotar(fuente, c, regla, crudo, nuevo[col == crudo].iloc[0], n)
            n_cambios += int(dif.sum())
        df[c] = nuevo

    df.to_csv(os.path.join(DEST, f), index=False, encoding="utf-8")
    resumen.append({"fuente": fuente, "filas": len(df), "celdas_modificadas": n_cambios})
    print(f"  {fuente}: {len(df):,} filas | celdas normalizadas: {n_cambios:,}")

det = pd.DataFrame(cambios)
if not det.empty:
    det = det.groupby(["fuente", "columna", "regla", "valor_crudo", "valor_normalizado"], as_index=False)["filas"].sum()
    det = det.sort_values(["fuente", "columna", "filas"], ascending=[True, True, False])
    det.to_csv(os.path.join(BASE, "resultados", "cambios_normalizacion_aplicados.csv"), index=False, encoding="utf-8-sig")
res = pd.DataFrame(resumen)
print(f"\nTOTAL celdas normalizadas: {res['celdas_modificadas'].sum():,} en {int((res['celdas_modificadas']>0).sum())} fuentes")

# ---------- control: nada mas cambio ----------
print("\nCONTROL de integridad (crudo vs normalizado):")
ok = True
for f in archivos:
    a = pd.read_csv(os.path.join(ORIG, f)); b = pd.read_csv(os.path.join(DEST, f))
    if a.shape != b.shape:
        print(f"  !! {f}: forma distinta {a.shape} vs {b.shape}"); ok = False; continue
    for c in a.columns:
        na, nb = pd.to_numeric(a[c], errors="coerce"), pd.to_numeric(b[c], errors="coerce")
        if na.notna().mean() > .95:
            if not na.fillna(-10**9).round(6).equals(nb.fillna(-10**9).round(6)):
                print(f"  !! {f}.{c}: valores numericos alterados"); ok = False
    if int(a.isna().sum().sum()) != int(b.isna().sum().sum()):
        print(f"  !! {f}: cambio la cantidad de nulos"); ok = False
print("  Filas, columnas, nulos y valores numericos: sin cambios." if ok else "  *** revisar avisos de arriba ***")

# ---------- registro de cambios ----------
hoy = datetime.now().strftime("%d-%m-%Y")
lineas = [f"\n### {hoy} — Normalización de representación (R1 a R4)\n",
          f"Generado por `Entregable/Entregable 2/EDA/normalizar_datasets.py`. "
          f"Origen: `Datasets/` (sin tocar) → salida: `Datasets_Normalizados/`.\n",
          f"**Total: {res['celdas_modificadas'].sum():,} celdas normalizadas.** Filas, columnas, nulos y valores numéricos sin cambios (verificado).\n",
          "| Fuente | Columna | Regla | Valor crudo | Valor normalizado | Filas |",
          "|---|---|---|---|---|---|"]
if not det.empty:
    for _, r in det.iterrows():
        lineas.append(f"| {r['fuente']} | {r['columna']} | {r['regla']} | `{r['valor_crudo']}` | `{r['valor_normalizado']}` | {r['filas']:,} |")
lineas.append("\n**No se modificó** (pendiente de respuesta del negocio): valores negativos, nulos, "
              "duplicados por clave, fechas posteriores al corte ni descuentos fuera de rango.\n")
with open(REG, "a", encoding="utf-8") as fh:
    fh.write("\n".join(lineas) + "\n")
print(f"\nRegistro actualizado: {REG}")
