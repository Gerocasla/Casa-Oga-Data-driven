"""Consistencia de representacion: el mismo valor escrito de formas distintas.
Recorre TODAS las columnas de los 15 CSV y agrupa los valores que, normalizados
(sin acentos, sin mayusculas, sin separadores ni espacios extra), son el mismo.
Genera ademas la tabla de mapeo propuesta valor_crudo -> valor_canonico.
"""
import os
import re
import json
import unicodedata
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(BASE, "..", "..", "..", "Datasets"))
RES = os.path.join(BASE, "resultados")
LOG = open(os.path.join(RES, "consistencia_valores_log.txt"), "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200); pd.set_option("display.max_columns", 30)

def sinacento(x):
    return "".join(c for c in unicodedata.normalize("NFKD", str(x)) if not unicodedata.combining(c))

def clave(x):
    """Forma canonica de comparacion: sin acentos, minusculas, sin separadores ni espacios."""
    k = sinacento(x).lower().strip()
    k = re.sub(r"[\s_\-\.]+", "", k)
    return k

data = {f[:-4]: pd.read_csv(os.path.join(DATA, f), dtype=str, keep_default_na=True)
        for f in sorted(os.listdir(DATA)) if f.endswith(".csv")}

P("=" * 110); P("1. MISMO VALOR ESCRITO DE DISTINTA FORMA (dentro de cada columna)"); P("=" * 110)
hallazgos = []
for n, df in data.items():
    for c in df.columns:
        col = df[c].dropna()
        if col.empty or col.nunique() > 3000:
            continue
        if pd.to_numeric(col, errors="coerce").notna().mean() > .95:
            continue  # columnas numericas: los negativos se analizan como outliers, no como variantes
        vc = col.value_counts()
        grupos = {}
        for val, cnt in vc.items():
            grupos.setdefault(clave(val), []).append((val, int(cnt)))
        malos = {k: v for k, v in grupos.items() if len(v) > 1}
        if malos:
            P(f"\n  {n}.{c}  ({col.nunique()} valores distintos, {len(malos)} grupo(s) con variantes)")
            for k, v in malos.items():
                v = sorted(v, key=lambda x: -x[1])
                P(f"     {' | '.join(f'{repr(a)} x{b}' for a, b in v)}   ->  canonico sugerido: {repr(v[0][0])}")
                for a, b in v[1:]:
                    hallazgos.append({"fuente": n, "columna": c, "valor_crudo": a, "filas": b,
                                      "valor_canonico": v[0][0], "tipo": "variante de escritura"})

P("\n" + "=" * 110); P("2. ESPACIOS, MAYUSCULAS Y CARACTERES RAROS"); P("=" * 110)
algo = False
for n, df in data.items():
    for c in df.columns:
        col = df[c].dropna().astype(str)
        if col.empty:
            continue
        esp = int((col != col.str.strip()).sum())
        dobles = int(col.str.contains(r"\s{2,}", regex=True).sum())
        raros = int(col.str.contains(r"[^\w\s\-\.,:/áéíóúñÁÉÍÓÚÑ°%$()+]", regex=True).sum())
        nobreak = int(col.str.contains(" ").sum())
        if esp or dobles or raros or nobreak:
            P(f"  {n}.{c}: espacios al borde {esp} | espacios dobles {dobles} | caracteres inusuales {raros} | espacio duro {nobreak}")
            algo = True
if not algo:
    P("  Ninguna columna tiene espacios sobrantes, espacios dobles ni caracteres raros.")

P("\n" + "=" * 110); P("3. FORMATOS DE FECHA"); P("=" * 110)
FECHAS = ["fecha", "fecha_mes", "fecha_alta_catalogo", "fecha_baja_catalogo", "fecha_inicio", "fecha_fin",
          "fecha_vigencia_desde", "fecha_vigencia_hasta", "fecha_pedido", "fecha_recepcion", "fecha_envio",
          "fecha_apertura"]
def patron(x):
    p = re.sub(r"\d", "9", str(x))
    return p
for n, df in data.items():
    for c in df.columns:
        if c in FECHAS:
            col = df[c].dropna().astype(str)
            pats = col.map(patron).value_counts()
            estado = "OK" if len(pats) == 1 else "*** MEZCLA DE FORMATOS ***"
            P(f"  {n}.{c}: {dict(pats)}  {estado}")
            if len(pats) > 1:
                for p_, k in pats.items():
                    if k < pats.max():
                        ej = col[col.map(patron) == p_].unique()[:8].tolist()
                        P(f"       formato minoritario {p_} ({k} filas): {ej}")
                        for e in col[col.map(patron) == p_].tolist():
                            hallazgos.append({"fuente": n, "columna": c, "valor_crudo": e, "filas": 1,
                                              "valor_canonico": e.split(" ")[0], "tipo": "formato de fecha"})

P("\n" + "=" * 110); P("4. FORMATOS DE IDENTIFICADOR Y DE NUMERO"); P("=" * 110)
for n, df in data.items():
    for c in df.columns:
        col = df[c].dropna().astype(str)
        if col.empty:
            continue
        if c.startswith("id_") or c in ("tienda", "origen", "destino", "proveedor"):
            pats = col.map(lambda x: re.sub(r"\d", "9", x)).value_counts()
            if len(pats) > 1:
                P(f"  {n}.{c}: {dict(list(pats.items())[:6])}")
        num = pd.to_numeric(col, errors="coerce")
        if num.notna().mean() > .95:
            dec = int(col.str.contains(",", regex=False).sum())
            cero = int(col.str.match(r"^0\d").sum())
            expo = int(col.str.contains(r"[eE]\d", regex=True).sum())
            if dec or cero or expo:
                P(f"  {n}.{c}: coma decimal {dec} | ceros a la izquierda {cero} | notacion cientifica {expo}")
P("  (si no aparece nada arriba: todos los IDs siguen un unico patron y los numeros usan punto decimal)")

P("\n" + "=" * 110); P("5. EL MISMO CONCEPTO ENTRE FUENTES DISTINTAS"); P("=" * 110)
def valores(n, c):
    return set(data[n][c].dropna().unique())

P("\n  a) CATEGORIA")
cats = {"Productos_catalogo": valores("Productos_catalogo", "categoria"),
        "Presupuesto_Ventas_Tienda_Categoria": valores("Presupuesto_Ventas_Tienda_Categoria", "categoria"),
        "Promociones_Comerciales": valores("Promociones_Comerciales", "categoria"),
        "Costo_almacenamiento": valores("Costo_almacenamiento", "categoria")}
for k, v in cats.items():
    P(f"     {k}: {len(v)} valores -> {sorted(v)}")
canon = sorted(cats["Costo_almacenamiento"])
P(f"     Canonico propuesto (el de Costo_almacenamiento y Presupuesto, sin acentos): {canon}")
for k, v in cats.items():
    fuera = {x for x in v if clave(x) not in {clave(y) for y in canon}}
    P(f"     {k}: valores que NO mapean a ninguna categoria canonica -> {sorted(fuera) if fuera else 'ninguno'}")

P("\n  b) TIENDA")
P(f"     Tiendas.id_tienda: {len(valores('Tiendas','id_tienda'))} ids, patron T99")
P(f"     Liquidaciones.tienda: {sorted(valores('Liquidaciones','tienda') - valores('Tiendas','id_tienda'))} (valor especial)")
P(f"     Transferencias.origen/destino: {sorted((valores('Transferencias_Stock','origen') | valores('Transferencias_Stock','destino')) - valores('Tiendas','id_tienda'))} (valor especial)")
prov_t = data["Tiendas"]["provincia"].unique()
P(f"     Tiendas.provincia: {sorted(prov_t)}")
nom = data["Tiendas"]["nombre_tienda"]
P("     nombre_tienda: patron 'Casa Óga <Provincia> <N>' en " + str(int(nom.str.match(r"^Casa Óga .+ \d+$").sum())) + " de 28")
incoh = [(r["id_tienda"], r["nombre_tienda"], r["provincia"]) for _, r in data["Tiendas"].iterrows()
         if clave(r["provincia"]) not in clave(r["nombre_tienda"]) and clave(r["provincia"]) != "caba"]
P(f"     Nombre de tienda que no coincide con su provincia: {incoh if incoh else 'ninguno'}")
ok_num = 0
for _, r in data["Tiendas"].iterrows():
    m = re.search(r"(\d+)$", str(r["nombre_tienda"]))
    if m and int(m.group(1)) == int(str(r["id_tienda"])[1:]):
        ok_num += 1
P("     Numero del nombre == numero del id: " + str(ok_num) + " de 28")

P("\n  c) PROVEEDOR")
P(f"     Proveedores: {sorted(valores('Proveedores','proveedor'))}")
for n in ["Productos_catalogo", "Ordenes_Compra"]:
    P(f"     {n}: {len(valores(n,'proveedor'))} valores, todos en el maestro: {valores(n,'proveedor') <= valores('Proveedores','proveedor')}")

P("\n  d) EVENTOS")
P(f"     Calendario.evento_especial: {sorted(valores('Calendario','evento_especial'))}")
P(f"     Promociones.evento_asociado: {sorted(valores('Promociones_Comerciales','evento_asociado'))}")
dif = {clave(x) for x in valores('Promociones_Comerciales', 'evento_asociado')} - {clave(x) for x in valores('Calendario', 'evento_especial')}
P(f"     Eventos de promociones que no existen en el calendario: {dif if dif else 'ninguno'}")

P("\n  e) MOTIVOS Y OTRAS LISTAS CERRADAS")
for n, c in [("Liquidaciones", "motivo"), ("Devoluciones_SKU", "motivo"), ("Promociones_Comerciales", "canal"),
             ("Promociones_Comerciales", "medio_pago"), ("Proveedores", "condicion_pago"), ("Proveedores", "pais_origen"),
             ("Tiendas", "formato"), ("Tiendas", "region"), ("Calendario", "temporada"), ("Calendario", "dia_semana"),
             ("Calendario", "es_feriado"), ("Productos_catalogo", "estado"), ("Productos_catalogo", "subcategoria")]:
    vals = sorted(valores(n, c))
    acent = [v for v in vals if sinacento(v) != v]
    P(f"     {n}.{c}: {len(vals)} valores | con acento: {acent if acent else 'ninguno'}")
    if len(vals) <= 12:
        P(f"        {vals}")

P("\n  f) IDIOMA Y ACENTUACION: la mezcla mas evidente")
P("     Calendario.dia_semana esta en INGLES (Monday, Tuesday...) mientras el resto del dataset esta en espaniol.")
P("     Las categorias 'Decoracion', 'Iluminacion', 'Organizacion' y 'Bano' aparecen SIN acento como forma mayoritaria,")
P("     pero 'Baño' si lleva enie y 'Casa Óga' lleva tilde: la convencion no es uniforme dentro del mismo dataset.")
acent_cols = []
for n, df in data.items():
    for c in df.columns:
        col = df[c].dropna().astype(str)
        if col.empty or col.nunique() > 3000:
            continue
        con = int(col.map(lambda x: sinacento(x) != x).sum())
        if 0 < con < len(col):
            acent_cols.append((n, c, con, len(col)))
for n, c, k, tot in acent_cols:
    P(f"     {n}.{c}: {k} de {tot} filas con acento (convive con filas sin acento)")

P("\n" + "=" * 110); P("6. TABLA DE NORMALIZACION PROPUESTA"); P("=" * 110)
h = pd.DataFrame(hallazgos)
if not h.empty:
    h = h.sort_values(["fuente", "columna", "filas"], ascending=[True, True, False])
    P(h.to_string(index=False))
    h.to_csv(os.path.join(RES, "mapeo_normalizacion.csv"), index=False, encoding="utf-8-sig")
    P(f"\n  Total de celdas a normalizar: {int(h['filas'].sum())} en {h.groupby(['fuente','columna']).ngroups} columnas")
    P(f"  Guardado en resultados/mapeo_normalizacion.csv")
LOG.close()
