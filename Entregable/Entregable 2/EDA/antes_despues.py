# -*- coding: utf-8 -*-
"""
Dashboard de calidad: metricas calculadas ANTES y DESPUES de aplicar el plan de mejora
(Entregable 2 · Parte B · 1.3).

ANTES   = Datasets/ tal como los entrega la catedra, con el calculo que haria un analista
          sin revisar calidad: suma todo, no deduplica, no trata negativos, ignora costos
          faltantes, usa las categorias como vienen. Si una clave esta duplicada, se suman
          sus filas (lo que hace un groupby sin control).
DESPUES = Datasets_Normalizados/ + criterios del plan de mejora (seccion 1.2):
          H1 dedup 1ra ocurrencia · H4 stock piso 0 y ventas neteadas · H9 descuentos y
          presupuesto invalidos excluidos · H11 costo OC x 1,2321 · R1 categorias · R2 fechas.

Salidas: resultados/antes_despues.csv · resultados/antes_despues.json ·
         graficos/13_antes_despues.png
         (el dashboard HTML lo arma Modelo/armar_dashboard.py)
"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
RAW, NRM = os.path.join(ROOT, "Datasets"), os.path.join(ROOT, "Datasets_Normalizados")
RES, GRA = os.path.join(BASE, "resultados"), os.path.join(BASE, "graficos")
K = ["fecha_mes", "id_tienda", "id_producto"]
FACTOR = 1.2321
M = 1e6

def rd(carpeta, f, **kw): return pd.read_csv(os.path.join(carpeta, f), **kw)

# ------------------------------------------------------------------ ANTES
v0 = rd(RAW, "Ventas_SKU_tienda_mensual.csv")
s0 = rd(RAW, "Stock_SKU_tienda_mensual.csv")
c0 = rd(RAW, "Productos_catalogo.csv")
l0 = rd(RAW, "Liquidaciones.csv")
p0 = rd(RAW, "Promociones_Comerciales.csv")
b0 = rd(RAW, "Presupuesto_Ventas_Tienda_Categoria.csv")

# ------------------------------------------------------------------ DESPUES
v1r = rd(NRM, "Ventas_SKU_tienda_mensual.csv")
pos = v1r[v1r["unidades_vendidas"] >= 0].drop_duplicates(K)
neg = v1r[v1r["unidades_vendidas"] < 0]
v1 = pd.concat([pos, neg]).groupby(K, as_index=False)[["unidades_vendidas", "venta_neta"]].sum()
s1 = rd(NRM, "Stock_SKU_tienda_mensual.csv").drop_duplicates(K)
s1["stock_disponible"] = s1["stock_disponible"].clip(lower=0)
c1 = rd(NRM, "Productos_catalogo.csv").drop_duplicates("id_producto")
oc = rd(NRM, "Ordenes_Compra.csv"); oc["m"] = oc["unidades"] * oc["costo_unitario_ars"]
c_oc = oc.groupby("id_producto")["m"].sum() / oc.groupby("id_producto")["unidades"].sum()
c1["costo_unitario"] = c1["costo_unitario"].fillna(c1["id_producto"].map(c_oc * FACTOR))
l1 = rd(NRM, "Liquidaciones.csv"); p1 = rd(NRM, "Promociones_Comerciales.csv")
b1 = rd(NRM, "Presupuesto_Ventas_Tienda_Categoria.csv")

filas = []
def add(grupo, metrica, antes, despues, fmt, impacto):
    filas.append(dict(grupo=grupo, metrica=metrica, antes=antes, despues=despues, fmt=fmt, impacto=impacto))
    print(f"{metrica:55s} {antes:>16,.2f} {despues:>16,.2f}")

# 1. volumen
add("Volumen", "Registros de venta (mes-tienda-SKU)", len(v0), len(v1), "n",
    "2.378 claves duplicadas (H1) se reducen a un registro por clave.")
add("Volumen", "Venta total ene-22 a ago-26 (M$)", v0["venta_neta"].sum() / M, v1["venta_neta"].sum() / M, "m",
    "Los duplicados inflan la venta; las devoluciones quedan neteadas, no perdidas.")
add("Volumen", "Unidades vendidas ene-22 a ago-26", v0["unidades_vendidas"].sum(), v1["unidades_vendidas"].sum(), "n",
    "Mismo efecto en unidades.")

# 2. stock y capital inmovilizado
for corte, et in [("2025-12-01", "dic-25"), ("2026-08-01", "ago-26")]:
    a = s0[s0["fecha_mes"] == corte]; b = s1[s1["fecha_mes"] == corte]
    if et == "dic-25":
        add("Stock", f"Filas con stock negativo (total)", int((s0["stock_disponible"] < 0).sum()),
            int((s1["stock_disponible"] < 0).sum()), "n", "Error de sincronizacion POS-inventario (P14): piso en 0.")
    cap0 = a.merge(c0[["id_producto", "costo_unitario"]], on="id_producto")          # catalogo con SKUs duplicados
    cap0 = (cap0["stock_disponible"] * cap0["costo_unitario"]).sum() / M                 # NaN (sin costo) se ignora
    cap1 = b.merge(c1[["id_producto", "costo_unitario"]], on="id_producto")
    cap1 = (cap1["stock_disponible"] * cap1["costo_unitario"]).sum() / M
    add("Stock", f"Capital inmovilizado en tiendas a {et} (M$ a costo)", cap0, cap1, "m",
        "Antes: SKUs duplicados cuentan doble, 22 SKUs sin costo valen 0. Despues: dedup + costo OC x 1,2321.")

# 3. categorias
add("Consistencia", "Valores distintos de categoria (catalogo)", c0["categoria"].nunique(), c1["categoria"].nunique(), "n",
    "R1: 11 variantes de escritura para 7 categorias reales.")
cat_v0 = v0.merge(c0.drop_duplicates("id_producto")[["id_producto", "categoria"]], on="id_producto")
cat_v1 = v1.merge(c1[["id_producto", "categoria"]], on="id_producto")
d0 = cat_v0[cat_v0["categoria"] == "Decoracion"]["venta_neta"].sum() / cat_v0["venta_neta"].sum() * 100
d1 = cat_v1[cat_v1["categoria"] == "Decoracion"]["venta_neta"].sum() / cat_v1["venta_neta"].sum() * 100
add("Consistencia", "Participacion de Decoracion en la venta (%)", d0, d1, "p",
    "Filtrar por la etiqueta mayoritaria (Decoracion) pierde los SKUs cargados como DECO o Decoración.")

# 4. descuentos
add("Validez", "Descuento promedio en liquidaciones (%)", l0["descuento_pct"].mean(),
    l1[l1["descuento_pct"].between(0, 100)]["descuento_pct"].mean(), "p",
    "3 valores fuera de rango (120, -10, 120) excluidos como error de carga (P24-P28).")
add("Validez", "Descuento promedio en promociones (%)", p0["descuento_pct"].mean(),
    p1[p1["descuento_pct"].between(0, 100)]["descuento_pct"].mean(), "p",
    "2 valores fuera de rango (150, -15) excluidos.")
fechas_ok0 = pd.to_datetime(l0["fecha_fin"], format="%Y-%m-%d", errors="coerce").notna().sum()
fechas_ok1 = pd.to_datetime(l1["fecha_fin"], format="%Y-%m-%d", errors="coerce").notna().sum()
add("Validez", "Liquidaciones con fecha de fin legible", fechas_ok0, fechas_ok1, "n",
    "R2: 8 fechas con hora recuperadas; el TP1 las habia descartado.")

# 5. presupuesto 2022
def cumplimiento(v, b, limpiar):
    vv = v.merge(c1[["id_producto", "categoria"]], on="id_producto")
    real = vv.groupby(["fecha_mes", "id_tienda", "categoria"])["venta_neta"].sum().reset_index()
    x = b.merge(real, on=["fecha_mes", "id_tienda", "categoria"], how="left").fillna({"venta_neta": 0})
    x = x[x["fecha_mes"].str.startswith("2022")]
    if limpiar: x = x[x["presupuesto_venta_ars"] > 0]
    return x["venta_neta"].sum() / x["presupuesto_venta_ars"].sum() * 100
b0n = b0.copy(); b0n["categoria"] = b1["categoria"]   # misma fila, solo para poder cruzar
add("Validez", "Cumplimiento presupuestario 2022 (%)", cumplimiento(v0, b0n, False), cumplimiento(v1, b1, True), "p",
    "309 celdas en cero (ene-may 22) y 3 negativas excluidas (P29-P32): antes la venta real sin meta infla el %.")

# 6. target del modelo y estado actual
def cob12(v, s, dic="2025-12-01"):
    d = s.groupby(K, as_index=False)[["stock_disponible"]].sum().merge(
        v.groupby(K, as_index=False)[["unidades_vendidas"]].sum(), on=K)
    d = d.sort_values(["id_tienda", "id_producto", "fecha_mes"])
    d["u12"] = d.groupby(["id_tienda", "id_producto"])["unidades_vendidas"].transform(lambda x: x.rolling(12, min_periods=1).mean())
    x = d[(d["fecha_mes"] == dic) & (d["stock_disponible"] > 0)]
    return int(((x["u12"] <= 0) | (x["stock_disponible"] / x["u12"].where(x["u12"] > 0) > 12)).sum())
add("Modelo", "Posiciones con cobertura > 12 meses a dic-25", cob12(v0, s0), cob12(v1, s1), "n",
    "Duplicados sumados y negativos sin tratar cambian el ritmo de venta y el stock de cada posicion.")
add("Modelo", "Prevalencia del target (cobertura > 12 a 3 meses, %)", 2.61, 3.40, "p",
    "Devoluciones llevadas a 0 (criterio previo) vs neteadas (default P23): 5.260 -> 6.853 positivos (+1.593). Fuente: EDA/candidatos_target.py.")

df = pd.DataFrame(filas)
df["variacion_pct"] = np.where(df["antes"] != 0, (df["despues"] / df["antes"] - 1) * 100, np.nan)
df.to_csv(os.path.join(RES, "antes_despues.csv"), index=False)

# series para graficos
anual = pd.DataFrame({
    "antes": v0.assign(a=v0["fecha_mes"].str[:4]).groupby("a")["venta_neta"].sum() / M,
    "despues": v1.assign(a=v1["fecha_mes"].str[:4]).groupby("a")["venta_neta"].sum() / M}).round(1)
cats0 = (cat_v0.groupby("categoria")["venta_neta"].sum() / M).round(1).sort_values(ascending=False)
cats1 = (cat_v1.groupby("categoria")["venta_neta"].sum() / M).round(1).sort_values(ascending=False)
neg_mes = pd.DataFrame({
    "stock_neg": s0[s0["stock_disponible"] < 0].groupby("fecha_mes").size(),
    "dup": v0[v0.duplicated(K, keep="first")].groupby("fecha_mes").size()}).fillna(0).astype(int)
neg_mes = neg_mes.reindex(sorted(s0["fecha_mes"].unique()), fill_value=0)
out = {"metricas": df.to_dict("records"),
       "anual": {"anios": list(anual.index), "antes": list(anual["antes"]), "despues": list(anual["despues"])},
       "cat_antes": {"labels": list(cats0.index), "valores": list(cats0.values)},
       "cat_despues": {"labels": list(cats1.index), "valores": list(cats1.values)},
       "problemas_mes": {"meses": list(neg_mes.index.str[:7]), "stock_neg": neg_mes["stock_neg"].tolist(),
                         "dup": neg_mes["dup"].tolist()}}
json.dump(out, open(os.path.join(RES, "antes_despues.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1,
          default=float)

# ------------------------------------------------------------------ PNG para el Word
ANT, DES, INK, MUT = "#9A9AA0", "#3E6FA8", "#1C1C1E", "#6E6E73"
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#E2E8F0", "axes.labelcolor": MUT, "xtick.color": MUT, "ytick.color": MUT})
fig, ax = plt.subplots(2, 2, figsize=(11, 7.2))
x = np.arange(len(anual)); w = 0.38
ax[0, 0].bar(x - w/2, anual["antes"], w, color=ANT, label="Antes"); ax[0, 0].bar(x + w/2, anual["despues"], w, color=DES, label="Después")
ax[0, 0].set_xticks(x, anual.index); ax[0, 0].set_title("Venta anual (M$)", loc="left", color=INK, fontweight="bold")
ax[0, 0].legend(frameon=False)
sel = df[df["metrica"].str.startswith("Capital")]
ax[0, 1].bar(np.arange(2) - w/2, sel["antes"], w, color=ANT, label="Antes"); ax[0, 1].bar(np.arange(2) + w/2, sel["despues"], w, color=DES, label="Después")
for i, (a_, d_) in enumerate(zip(sel["antes"], sel["despues"])):
    ax[0, 1].text(i - w/2, a_, f"{a_:,.0f}", ha="center", va="bottom", color=MUT, fontsize=8)
    ax[0, 1].text(i + w/2, d_, f"{d_:,.0f}", ha="center", va="bottom", color=INK, fontsize=8)
ax[0, 1].set_xticks(range(2), ["dic-25", "ago-26"]); ax[0, 1].set_title("Capital inmovilizado a costo (M$)", loc="left", color=INK, fontweight="bold")
ax[1, 0].barh(cats0.index[::-1], cats0.values[::-1], color=ANT); ax[1, 0].set_title("Venta por categoría ANTES (M$) · 11 valores", loc="left", color=INK, fontweight="bold")
ax[1, 1].barh(cats1.index[::-1], cats1.values[::-1], color=DES); ax[1, 1].set_title("Venta por categoría DESPUÉS (M$) · 7 valores", loc="left", color=INK, fontweight="bold")
for a in ax.flat: a.grid(axis="y" if a in (ax[0, 0], ax[0, 1]) else "x", color="#E8EDF3"); a.set_axisbelow(True)
fig.tight_layout(); fig.savefig(os.path.join(GRA, "13_antes_despues.png"), dpi=170); plt.close(fig)

print("OK: resultados/antes_despues.csv/json y graficos/13_antes_despues.png (el HTML lo arma Modelo/armar_dashboard.py)")
