"""Compara variables objetivo candidatas para el modelo (horizonte 3 meses).
Grano: SKU-tienda-mes. Universo: posiciones con stock > 0 en el mes t.
Etiqueta: estado de esa misma posicion en t+3.
"""
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(BASE, "..", "..", "..", "Datasets_Normalizados"))
LOG = open(os.path.join(BASE, "resultados", "candidatos_target_log.txt"), "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n")
K = ["fecha_mes", "id_tienda", "id_producto"]

v = pd.read_csv(os.path.join(DATA, "Ventas_SKU_tienda_mensual.csv")).drop_duplicates(K)
s = pd.read_csv(os.path.join(DATA, "Stock_SKU_tienda_mensual.csv")).drop_duplicates(K)
cat = pd.read_csv(os.path.join(DATA, "Productos_catalogo.csv")).drop_duplicates("id_producto")
v[["unidades_vendidas", "venta_neta"]] = v[["unidades_vendidas", "venta_neta"]].clip(lower=0)
s["stock_disponible"] = s["stock_disponible"].clip(lower=0)
d = s.merge(v, on=K)
d["fecha_mes"] = pd.to_datetime(d["fecha_mes"])
d = d.sort_values(["id_tienda", "id_producto", "fecha_mes"])
g = d.groupby(["id_tienda", "id_producto"], sort=False)

# --- variables de estado ---
d["u12"] = g["unidades_vendidas"].transform(lambda x: x.rolling(12, min_periods=1).mean())
d["u3"] = g["unidades_vendidas"].transform(lambda x: x.rolling(3, min_periods=3).sum())
d["cobertura"] = np.where(d["u12"] > 0, d["stock_disponible"] / d["u12"].replace(0, np.nan), np.inf)
baja = cat.set_index("id_producto")["fecha_baja_catalogo"]
d["baja"] = pd.to_datetime(d["id_producto"].map(baja))
d["fin_mes"] = d["fecha_mes"] + pd.offsets.MonthEnd(0)
d["discontinuado"] = d["baja"].notna() & (d["baja"] <= d["fin_mes"])
d["con_stock"] = d["stock_disponible"] > 0

# --- candidatos de estado en un mes dado ---
d["A_deadstock"] = d["con_stock"] & ((d["u3"] == 0) | (d["cobertura"] > 12) | d["discontinuado"])
d["B_rojo"] = d["con_stock"] & ((d["cobertura"] > 12) | d["discontinuado"])
d["C_sin_venta3"] = d["con_stock"] & (d["u3"] == 0)
d["D_cob12"] = d["con_stock"] & (d["cobertura"] > 12) & ~d["discontinuado"]
d["E_cob9"] = d["con_stock"] & (d["cobertura"] > 9) & ~d["discontinuado"]

# --- etiqueta a 3 meses ---
CAND = ["A_deadstock", "B_rojo", "C_sin_venta3", "D_cob12", "E_cob9"]
NOMBRE = {"A_deadstock": "A · Dead stock binario (3 condiciones OR)",
          "B_rojo": "B · Banda roja (cobertura>12 o discontinuado)",
          "C_sin_venta3": "C · Sin ventas en 3 meses",
          "D_cob12": "D · Cobertura>12 meses (sin discontinuados)",
          "E_cob9": "E · Cobertura>9 meses (rojo + amarillo)"}
for c in CAND:
    d[c + "_t3"] = g[c].shift(-3)
d["mes_t3"] = g["fecha_mes"].shift(-3)
# la fila t+3 tiene que ser realmente 3 meses despues
valido = (d["mes_t3"] - d["fecha_mes"]).dt.days.between(85, 95)
d["u12_valido"] = g.cumcount() >= 11   # al menos 12 meses de historia

base = d[valido & d["u12_valido"] & d["con_stock"]].copy()
P(f"Universo de entrenamiento: {len(base):,} filas (posicion con stock, 12m de historia y etiqueta a 3 meses)")
P(f"Periodo de los cortes: {base['fecha_mes'].min().date()} a {base['fecha_mes'].max().date()} | "
  f"posiciones distintas: {base.groupby(['id_tienda','id_producto']).ngroups:,}\n")

filas = []
for c in CAND:
    y = base[c + "_t3"].astype(bool)
    hoy = base[c].astype(bool)
    sanos = base[~hoy]
    y_sanos = sanos[c + "_t3"].astype(bool)
    enfermos = base[hoy]
    y_enf = enfermos[c + "_t3"].astype(bool)
    filas.append({
        "candidato": NOMBRE[c],
        "positivos_t3": f"{y.mean():.2%}",
        "n_positivos": f"{int(y.sum()):,}",
        "ya_positivo_en_t": f"{hoy.mean():.2%}",
        "SE_VUELVE_positivo (de sanos)": f"{y_sanos.mean():.2%}" if len(sanos) else "-",
        "n_nuevos": f"{int(y_sanos.sum()):,}",
        "SIGUE_positivo (de enfermos)": f"{y_enf.mean():.2%}" if len(enfermos) else "-",
        "info_nueva_%": f"{y_sanos.sum() / max(y.sum(), 1):.1%}"})
res = pd.DataFrame(filas)
P("COMPARACION DE CANDIDATOS (etiqueta = estado de la posicion 3 meses despues)")
P(res.to_string(index=False))
P("\n  positivos_t3     = prevalencia de la clase positiva (cuanto pesa el target)")
P("  ya_positivo_en_t = cuantas posiciones ya estaban en ese estado al momento de predecir")
P("  SE_VUELVE        = de las sanas hoy, cuantas caen en 3 meses  -> ESTO es lo que el modelo tiene que anticipar")
P("  SIGUE            = de las que ya estan, cuantas siguen        -> mide inercia / persistencia")
P("  info_nueva_%     = que porcion de los positivos son casos NUEVOS y no arrastre del estado actual")

P("\n" + "=" * 100)
P("DETALLE DEL CANDIDATO B (banda roja) — el que proponemos")
P("=" * 100)
c = "B_rojo"
y = base[c + "_t3"].astype(bool); hoy = base[c].astype(bool)
P(f"  Positivos: {int(y.sum()):,} de {len(base):,} ({y.mean():.2%})")
P(f"  Matriz de transicion t -> t+3:")
P(f"    sano   -> sano   : {int((~hoy & ~y).sum()):>7,}   ({(~hoy & ~y).mean():6.2%})")
P(f"    sano   -> EN RIESGO: {int((~hoy & y).sum()):>5,}   ({(~hoy & y).mean():6.2%})   <- casos a predecir")
P(f"    riesgo -> sano   : {int((hoy & ~y).sum()):>7,}   ({(hoy & ~y).mean():6.2%})")
P(f"    riesgo -> riesgo : {int((hoy & y).sum()):>7,}   ({(hoy & y).mean():6.2%})")
P(f"\n  Descomposicion de los positivos en t+3:")
sub = base[y]
disc = sub[c.replace("B_rojo", "")] if False else None
d3 = base.assign(_y=y)
P(f"    por cobertura > 12 meses : {int((base['D_cob12'].shift(0) & y).sum()):,} (aprox, medido en t)")
P(f"    posiciones distintas involucradas: {sub.groupby(['id_tienda','id_producto']).ngroups:,}")
P(f"    SKUs distintos: {sub['id_producto'].nunique()} | tiendas: {sub['id_tienda'].nunique()}")
P(f"\n  Por anio del corte t:")
tt = base.assign(_y=y).groupby(base["fecha_mes"].dt.year)["_y"].agg(["size", "sum", "mean"])
tt.columns = ["filas", "positivos", "tasa"]; tt["tasa"] = (tt["tasa"] * 100).round(2)
P(tt.to_string())
P(f"\n  Posiciones por mes de corte (ultimos 6):")
P(base.groupby("fecha_mes").size().tail(6).to_string())

P("\n" + "=" * 100)
P("CONTROL: cuanto se explica con solo mirar el estado actual (modelo trivial)")
P("=" * 100)
for c in CAND:
    y = base[c + "_t3"].astype(bool); hoy = base[c].astype(bool)
    vp = int((hoy & y).sum()); fp = int((hoy & ~y).sum()); fn = int((~hoy & y).sum())
    prec = vp / max(vp + fp, 1); rec = vp / max(vp + fn, 1)
    P(f"  {NOMBRE[c]:48s} -> regla 'ya esta en ese estado': precision {prec:.1%} | recall {rec:.1%}")
P("\n  Si esa regla trivial ya tiene recall alto, el modelo aporta poco: el target es pura inercia.")
LOG.close()
