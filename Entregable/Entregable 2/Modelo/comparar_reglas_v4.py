# -*- coding: utf-8 -*-
"""
Cuanto cambia el target al pasar de la v3 a la v4 (feedback de Casa Oga y de la catedra sobre el Entregable 2).

Escenarios (mismo universo y misma definicion de target que construir_dataset_modelo.py):
  v3                 dedup 1ra ocurrencia · todas las devoluciones neteadas
  dedup              dedup "mayor venta" (P4 del relevamiento) · todas neteadas
  sin_rotacion       dedup 1ra ocurrencia · sin neteo del motivo "sin rotacion / no vendido"
  v4                 dedup "mayor venta" + sin neteo de "sin rotacion"

Salidas: resultados/comparar_reglas_v4_log.txt · resultados/comparar_reglas_v4.csv
"""
import os, sys
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "EDA"))
from criterios_limpieza import limpiar_ventas_stock, K

ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
DATA = os.path.join(ROOT, "Datasets_Normalizados")
RES = os.path.join(BASE, "resultados")
LOG = open(os.path.join(RES, "comparar_reglas_v4_log.txt"), "w", encoding="utf-8")
def P(*a):
    t = " ".join(str(x) for x in a); print(t); LOG.write(t + "\n")

v_raw = pd.read_csv(os.path.join(DATA, "Ventas_SKU_tienda_mensual.csv"))
s_raw = pd.read_csv(os.path.join(DATA, "Stock_SKU_tienda_mensual.csv"))
dev = pd.read_csv(os.path.join(DATA, "Devoluciones_SKU.csv"))
cat = pd.read_csv(os.path.join(DATA, "Productos_catalogo.csv")).drop_duplicates("id_producto")
oc = pd.read_csv(os.path.join(DATA, "Ordenes_Compra.csv")); oc["m"] = oc["unidades"] * oc["costo_unitario_ars"]
costo = cat.set_index("id_producto")["costo_unitario"].fillna(
    oc.groupby("id_producto")["m"].sum() / oc.groupby("id_producto")["unidades"].sum() * 1.2321)
baja = pd.to_datetime(cat.set_index("id_producto")["fecha_baja_catalogo"])

def particion(m):
    if m <= pd.Timestamp("2024-12-01"): return "train"
    if pd.Timestamp("2025-04-01") <= m <= pd.Timestamp("2025-09-01"): return "validacion"
    if m >= pd.Timestamp("2026-01-01"): return "test"
    return "embargo"

def target(v, s):
    d = s.merge(v, on=K); d["fecha_mes"] = pd.to_datetime(d["fecha_mes"])
    d = d.sort_values(["id_tienda", "id_producto", "fecha_mes"]).reset_index(drop=True)
    g = d.groupby(["id_tienda", "id_producto"], sort=False)
    u12 = g["unidades_vendidas"].transform(lambda x: x.rolling(12, min_periods=1).mean())
    d["cobertura"] = np.where(u12 > 0, d["stock_disponible"] / u12.where(u12 > 0), np.inf)
    disc = d["id_producto"].map(baja).notna() & (d["id_producto"].map(baja) <= d["fecha_mes"] + pd.offsets.MonthEnd(0))
    con = d["stock_disponible"] > 0
    d["pos"] = con & (d["cobertura"] > 12) & ~disc
    y = g["pos"].shift(-3); m3 = g["fecha_mes"].shift(-3)
    univ = (m3 - d["fecha_mes"]).dt.days.between(85, 95) & (g.cumcount() >= 2) & con & ~disc
    ds = d[univ].assign(y=y[univ].astype(int))
    ds["split"] = ds["fecha_mes"].map(particion)
    return ds

ESC = {"v3": ("primera", False), "dedup": ("mayor_venta", False),
       "sin_rotacion": ("primera", True), "v4": ("mayor_venta", True)}
filas, dss, limp = [], {}, {}
for nombre, (regla, excl) in ESC.items():
    info = {}
    v, s = limpiar_ventas_stock(v_raw, s_raw, dev, regla=regla, excluir_sin_rotacion=excl, info=info)
    ds = target(v, s); dss[nombre] = ds; limp[nombre] = (v, s, info)
    tr = ds[ds["split"] == "train"]
    f = dict(escenario=nombre, venta_M=v["venta_neta"].sum() / 1e6, unidades=int(v["unidades_vendidas"].sum()),
             filas=len(ds), positivos=int(ds["y"].sum()), prevalencia=ds["y"].mean() * 100,
             peso_clase=(1 - tr["y"].mean()) / tr["y"].mean())
    for sp in ["train", "validacion", "test", "embargo"]:
        x = ds[ds["split"] == sp]; f[f"filas_{sp}"] = len(x); f[f"pos_{sp}"] = int(x["y"].sum()); f[f"prev_{sp}"] = x["y"].mean() * 100
    filas.append(f)
tab = pd.DataFrame(filas).set_index("escenario")
assert tab.loc["v3", "filas"] == 201306 and tab.loc["v3", "positivos"] == 6853, "no reproduce la v3"
tab.round(3).to_csv(os.path.join(RES, "comparar_reglas_v4.csv"))
P("=" * 100); P("TARGET Y PESO DE CLASE SEGUN LA REGLA (universo y target de construir_dataset_modelo.py)"); P("=" * 100)
P(tab.round(3).T.to_string())

# ------------------------------------------------------------------ detalle de la regla de deduplicacion
P("\n" + "=" * 100); P("H1 · 1RA OCURRENCIA vs MAYOR VENTA (P4)"); P("=" * 100)
pos = v_raw[v_raw["unidades_vendidas"] >= 0]
dk = pos[pos.duplicated(K, keep=False)]
P(f"Claves con dos registros de venta no negativos: {dk[K].drop_duplicates().shape[0]:,}")
prim = pos.drop_duplicates(K)
mayor = pos.sort_values("venta_neta", ascending=False, kind="mergesort").drop_duplicates(K)
cmp_ = prim.merge(mayor, on=K, suffixes=("_1ra", "_mayor"))
cambia = cmp_[cmp_["venta_neta_1ra"] != cmp_["venta_neta_mayor"]]
P(f"Claves donde la regla elige otro registro: {len(cambia):,} (en las demas, la 1ra ya es la de mayor venta o son iguales)")
P(f"  1ra ocurrencia en cero y la otra con venta: {int(((cambia['unidades_vendidas_1ra'] == 0)).sum()):,}")
P(f"  unidades: {int(cambia['unidades_vendidas_1ra'].sum()):,} -> {int(cambia['unidades_vendidas_mayor'].sum()):,} "
  f"(+{int(cambia['unidades_vendidas_mayor'].sum() - cambia['unidades_vendidas_1ra'].sum()):,})")
P(f"  venta: ${cambia['venta_neta_1ra'].sum()/1e6:,.1f} M -> ${cambia['venta_neta_mayor'].sum()/1e6:,.1f} M")
v3v, v3s, _ = limp["v3"]; ddv, dds, _ = limp["dedup"]
P(f"Venta total ene-22 a ago-26: ${v3v['venta_neta'].sum()/1e6:,.1f} M -> ${ddv['venta_neta'].sum()/1e6:,.1f} M "
  f"({(ddv['venta_neta'].sum()/v3v['venta_neta'].sum()-1)*100:+.2f}%) · unidades {int(v3v['unidades_vendidas'].sum()):,} -> {int(ddv['unidades_vendidas'].sum()):,}")
m = v3s.merge(dds, on=K, suffixes=("_v3", "_n"))
P(f"Stock: claves con otro valor de stock disponible: {int((m['stock_disponible_v3'] != m['stock_disponible_n']).sum()):,} · "
  f"unidades totales {int(m['stock_disponible_v3'].sum()):,} -> {int(m['stock_disponible_n'].sum()):,}")
for corte in ["2025-12-01", "2026-08-01"]:
    a = m[m["fecha_mes"] == corte]
    P(f"  capital a costo {corte[:7]}: ${(a['stock_disponible_v3'] * a['id_producto'].map(costo)).sum()/1e6:,.1f} M -> "
      f"${(a['stock_disponible_n'] * a['id_producto'].map(costo)).sum()/1e6:,.1f} M")
a3, ad = dss["v3"].set_index(K[:0] + ["fecha_mes", "id_tienda", "id_producto"]), dss["dedup"].set_index(["fecha_mes", "id_tienda", "id_producto"])
j = a3[["y"]].join(ad[["y"]], how="outer", lsuffix="_v3", rsuffix="_n")
P(f"Filas del universo: solo en v3 {int(j['y_n'].isna().sum()):,} · solo con la regla nueva {int(j['y_v3'].isna().sum()):,} · "
  f"cambian de clase {int(((j['y_v3'] != j['y_n']) & j.notna().all(axis=1)).sum()):,} "
  f"(0->1: {int(((j['y_v3'] == 0) & (j['y_n'] == 1)).sum()):,} · 1->0: {int(((j['y_v3'] == 1) & (j['y_n'] == 0)).sum()):,})")
sku_dup = set(v_raw[v_raw.duplicated(K, keep=False)]["id_producto"])
P(f"  todas las filas que cambian son de los {len(sku_dup)} SKUs duplicados: "
  f"{set(j[(j['y_v3'] != j['y_n'])].index.get_level_values('id_producto')) <= sku_dup}")

# ------------------------------------------------------------------ detalle del motivo sin rotacion
P("\n" + "=" * 100); P("H4 · NETEO SIN EL MOTIVO «SIN ROTACION / NO VENDIDO» (P18-P19)"); P("=" * 100)
_, _, inf4 = limp["v4"]
P(f"Filas de devolucion con ese motivo: {inf4['sin_rotacion_filas']:,} de 2.317 · {inf4['sin_rotacion_unidades']:,} unidades · "
  f"${inf4['sin_rotacion_venta']/1e6:,.1f} M (dejan de restarse de la venta)")
srv, _, _ = limp["sin_rotacion"]
P(f"Venta total: ${v3v['venta_neta'].sum()/1e6:,.1f} M -> ${srv['venta_neta'].sum()/1e6:,.1f} M · unidades "
  f"{int(v3v['unidades_vendidas'].sum()):,} -> {int(srv['unidades_vendidas'].sum()):,}")
b3, bs = dss["v3"].set_index(["fecha_mes", "id_tienda", "id_producto"]), dss["sin_rotacion"].set_index(["fecha_mes", "id_tienda", "id_producto"])
j2 = b3[["y"]].join(bs[["y"]], how="outer", lsuffix="_v3", rsuffix="_n")
P(f"Filas que cambian de clase: {int((j2['y_v3'] != j2['y_n']).sum()):,} (1->0: {int(((j2['y_v3'] == 1) & (j2['y_n'] == 0)).sum()):,} · "
  f"0->1: {int(((j2['y_v3'] == 0) & (j2['y_n'] == 1)).sum()):,})")
P("\nRESUMEN v3 -> v4")
for c in ["filas", "positivos", "prevalencia", "peso_clase", "prev_train", "prev_validacion", "prev_test"]:
    P(f"  {c:16s} {tab.loc['v3', c]:>12,.3f} -> {tab.loc['v4', c]:>12,.3f}")
LOG.close()
