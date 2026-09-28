# -*- coding: utf-8 -*-
"""
EDA de la Parte A recalculado al corte ago-2026 sobre Datasets_Normalizados, con los criterios
de limpieza vigentes (plan de mejora de la Parte B): dedup 1ra ocurrencia, stock con piso en 0,
ventas negativas neteadas, categorias unificadas, costo OC x 1,2321 para los 22 SKUs sin costo.

Reemplaza a eda.py (corte dic-2025) como fuente de los numeros y graficos de la Parte A.
Salidas: resultados/eda_ago26_log.txt · resultados/eda_ago26.json · graficos_ago26/G01..G12.png
"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(BASE, "..", "..", "..", "Datasets_Normalizados"))
RES = os.path.join(BASE, "resultados"); GRA = os.path.join(BASE, "graficos_ago26")
os.makedirs(GRA, exist_ok=True)
LOG = open(os.path.join(RES, "eda_ago26_log.txt"), "w", encoding="utf-8")
def P(*a):
    t = " ".join(str(x) for x in a); print(t); LOG.write(t + "\n")
def H(t): P("\n" + "=" * 90 + "\n" + t + "\n" + "=" * 90)
K = ["fecha_mes", "id_tienda", "id_producto"]; M = 1e6
OUT = {}
rd = lambda f, **kw: pd.read_csv(os.path.join(DATA, f), **kw)

# ------------------------------------------------------------------ carga
raw = {f[:-4]: rd(f) for f in sorted(os.listdir(DATA)) if f.endswith(".csv")}
H("A · PERFIL")
for n, df in raw.items(): P(f"  {n:38s} {len(df):>8,} filas")
OUT["filas"] = {n: len(df) for n, df in raw.items()}

v_raw = raw["Ventas_SKU_tienda_mensual"]
pos = v_raw[v_raw["unidades_vendidas"] >= 0].drop_duplicates(K)
neg = v_raw[v_raw["unidades_vendidas"] < 0]
ven = pd.concat([pos, neg]).groupby(K, as_index=False)[["unidades_vendidas", "venta_neta"]].sum()
sto = raw["Stock_SKU_tienda_mensual"].drop_duplicates(K).copy()
sto["stock_disponible"] = sto["stock_disponible"].clip(lower=0)
cat = raw["Productos_catalogo"].drop_duplicates("id_producto").copy()
tie = raw["Tiendas"]; prov = raw["Proveedores"]
for df in (ven, sto): df["fecha_mes"] = pd.to_datetime(df["fecha_mes"])
ven = ven.merge(cat[["id_producto", "categoria", "precio_lista", "costo_unitario"]], on="id_producto") \
         .merge(tie[["id_tienda", "region", "m2_venta"]], on="id_tienda")
ULT = ven["fecha_mes"].max()
P(f"  Ventas/Stock: {ven['fecha_mes'].min().date()} a {ULT.date()} ({ven['fecha_mes'].nunique()} meses)")
for n, col in [("Devoluciones_SKU", "fecha"), ("Calendario", "fecha"), ("Liquidaciones", "fecha_inicio"),
               ("Presupuesto_Ventas_Tienda_Categoria", "fecha_mes"), ("Promociones_Comerciales", "fecha_inicio"),
               ("Ordenes_Compra", "fecha_pedido"), ("Transferencias_Stock", "fecha_envio"),
               ("Stock_Deposito_Central", "fecha_mes"), ("Historial_Precios_SKU", "fecha_vigencia_desde"),
               ("Productos_catalogo", "fecha_alta_catalogo")]:
    P(f"  {n:38s} {raw[n][col].min()} -> {raw[n][col].max()}")
P(f"  SKUs catalogo: {cat['id_producto'].nunique()} | con venta: {ven[ven['unidades_vendidas'] != 0]['id_producto'].nunique()} | "
  f"categorias {cat['categoria'].nunique()} | subcategorias {cat['subcategoria'].nunique()}")

# ------------------------------------------------------------------ B · estadisticas
H("B · ESTADISTICAS (ultimos 12 meses: sep-25 a ago-26)")
u12m = ven[ven["fecha_mes"] > ULT - pd.DateOffset(months=12)]
q = [.25, .5, .75, .95, .99]
st_u = u12m["unidades_vendidas"].describe(percentiles=q); st_v = u12m["venta_neta"].describe(percentiles=q)
P("  unidades:", st_u.round(2).to_dict()); P("  venta   :", st_v.round(0).to_dict())
s_ult = sto[sto["fecha_mes"] == ULT]; s_pos = s_ult[s_ult["stock_disponible"] > 0]
st_s = s_pos["stock_disponible"].describe(percentiles=q)
P("  stock ago-26 (>0):", st_s.round(1).to_dict(), "| posiciones con stock:", len(s_pos))
baja = pd.to_datetime(cat.set_index("id_producto")["fecha_baja_catalogo"])
skus_st = s_pos["id_producto"].unique()
disc = int((baja.reindex(skus_st).notna()).sum())
P(f"  SKUs con stock ago-26: {len(skus_st)} (discontinuados: {disc})")
cero = (ven["unidades_vendidas"] == 0).mean()
vs = ven.merge(sto, on=K)
P(f"  filas con 0 unidades: {cero:.2%} | venta>0 y stock=0: {int(((vs.unidades_vendidas > 0) & (vs.stock_disponible == 0)).sum()):,}")
OUT["stats"] = dict(u=st_u.round(2).to_dict(), v=st_v.round(0).to_dict(), s=st_s.round(1).to_dict(),
                    pos_stock=len(s_pos), skus_stock=len(skus_st), skus_stock_disc=disc, pct_cero=round(cero * 100, 2))

# ------------------------------------------------------------------ C · evolucion
H("C · EVOLUCION")
mens = ven.groupby("fecha_mes").agg(venta=("venta_neta", "sum"), uds=("unidades_vendidas", "sum"),
                                    pos=("unidades_vendidas", "size"))
mens["stock"] = sto.groupby("fecha_mes")["stock_disponible"].sum()
mens["uds_pos"] = mens["uds"] / mens["pos"]
anual = ven.groupby(ven["fecha_mes"].dt.year).agg(venta=("venta_neta", "sum"), uds=("unidades_vendidas", "sum"))
P("  Venta por año ($M):", (anual["venta"] / M).round(1).to_dict())
P(f"  Total: ${ven['venta_neta'].sum()/M:,.1f} M · {ven['unidades_vendidas'].sum():,.0f} uds · precio medio ${ven['venta_neta'].sum()/ven['unidades_vendidas'].sum():,.0f}")
# interanual en BRUTO (sin devoluciones): 2026 no trae devoluciones (H12), netear solo 2025 sesgaria la comparacion
bru = pos.copy(); bru["fecha_mes"] = pd.to_datetime(bru["fecha_mes"])
a26 = bru[(bru["fecha_mes"] >= "2026-01-01")]; a25 = bru[(bru["fecha_mes"] >= "2025-01-01") & (bru["fecha_mes"] <= "2025-08-01")]
neto26 = ven[ven["fecha_mes"] >= "2026-01-01"]["venta_neta"].sum(); neto25 = ven[(ven["fecha_mes"] >= "2025-01-01") & (ven["fecha_mes"] <= "2025-08-01")]["venta_neta"].sum()
P(f"  (neteado: {neto26/neto25-1:+.1%} — no comparable, 2026 no tiene devoluciones registradas)")
var_v = a26["venta_neta"].sum() / a25["venta_neta"].sum() - 1
var_u = a26["unidades_vendidas"].sum() / a25["unidades_vendidas"].sum() - 1
pos26 = mens.loc["2026", "pos"].mean(); pos25 = mens.loc["2025-01":"2025-08", "pos"].mean()
P(f"  ene-ago 26 vs ene-ago 25: venta {var_v:+.1%} · unidades {var_u:+.1%} · posiciones con venta {pos26/pos25-1:+.1%}")
P(f"  posiciones con venta: ene-22 {mens['pos'].iloc[0]} · dic-25 {mens.loc['2025-12-01','pos']} · ene-26 {mens.loc['2026-01-01','pos']} · ago-26 {mens['pos'].iloc[-1]}")
P(f"  uds por posicion: min {mens['uds_pos'].min():.2f} max {mens['uds_pos'].max():.2f} · 2026 prom {mens.loc['2026','uds_pos'].mean():.2f}")
# estacionalidad ajustada por tendencia (media movil centrada de 12 meses)
mm = mens["venta"].rolling(12, center=True).mean()
adj = (mens["venta"] / mm * 100).dropna()
idx_adj = adj.groupby(adj.index.month).mean()
naive = mens.loc["2023":"2025"].copy(); naive["i"] = naive.groupby(naive.index.year)["venta"].transform(lambda x: x / x.mean() * 100)
idx_naive = naive.groupby(naive.index.month)["i"].mean()
P(f"  estacionalidad ingenua (prom anual): {idx_naive.min():.0f}-{idx_naive.max():.0f} | ajustada por tendencia: {idx_adj.min():.0f}-{idx_adj.max():.0f}")
OUT["evol"] = dict(anual={int(k): round(v / M, 1) for k, v in anual["venta"].items()}, var_v=var_v, var_u=var_u,
                   var_pos=pos26 / pos25 - 1, total=ven["venta_neta"].sum() / M, uds=int(ven["unidades_vendidas"].sum()),
                   idx_adj=(round(idx_adj.min()), round(idx_adj.max())), idx_naive=(round(idx_naive.min()), round(idx_naive.max())),
                   pos_dic25=int(mens.loc["2025-12-01", "pos"]), pos_ene26=int(mens.loc["2026-01-01", "pos"]), pos_ago26=int(mens["pos"].iloc[-1]))

# ------------------------------------------------------------------ D · dimensiones
H("D · DIMENSIONES (ene-22 a ago-26)")
tot = ven["venta_neta"].sum()
bycat = ven.groupby("categoria").agg(venta=("venta_neta", "sum"))
bycat["pct"] = bycat["venta"] / tot * 100
bycat["pct_sku"] = cat.groupby("categoria").size() / len(cat) * 100
bycat["margen"] = cat.assign(m=1 - cat.costo_unitario / cat.precio_lista).groupby("categoria")["m"].mean() * 100
bycat = bycat.sort_values("pct", ascending=False)
P(bycat.round(1).to_string())
byreg = ven.groupby("region")["venta_neta"].sum().div(tot).mul(100).sort_values(ascending=False)
ntie = tie.groupby("region").size()
P("  region:", {r: f"{v:.1f}% ({ntie[r]})" for r, v in byreg.items()})
byt = ven.groupby("id_tienda")["venta_neta"].sum()
bt = pd.DataFrame({"venta": byt / M, "pct": byt / tot * 100}).join(tie.set_index("id_tienda")[["m2_venta", "formato"]])
corr_m2 = bt["venta"].corr(bt["m2_venta"])
P(f"  tienda: {bt['pct'].min():.1f}%-{bt['pct'].max():.1f}% · max {bt['venta'].idxmax()} ${bt['venta'].max():,.0f} M · min {bt['venta'].idxmin()} ${bt['venta'].min():,.0f} M · corr m2 {corr_m2:.2f}")
bysku = ven.groupby("id_producto")["venta_neta"].sum().sort_values(ascending=False)
bysku = bysku[bysku > 0]; cum = bysku.cumsum() / bysku.sum()
n80 = int((cum < 0.8).sum() + 1); top10 = cum.iloc[int(len(bysku) * .1) - 1]
P(f"  Pareto: {n80} de {len(bysku)} SKUs = 80% ({n80/len(bysku):.1%}) · top 10% = {top10:.1%}")
margen_prom = (1 - cat.costo_unitario / cat.precio_lista).mean() * 100
OUT["dim"] = dict(cat=bycat.round(1).reset_index().to_dict("records"), reg={r: round(v, 1) for r, v in byreg.items()},
                  ntie=ntie.to_dict(), tmin=round(bt["pct"].min(), 1), tmax=round(bt["pct"].max(), 1),
                  tmax_id=bt["venta"].idxmax(), tmax_v=round(bt["venta"].max()), tmin_id=bt["venta"].idxmin(),
                  tmin_v=round(bt["venta"].min()), corr_m2=round(corr_m2, 2), n80=n80, nsku=len(bysku),
                  top10=round(top10 * 100, 1), margen=round(margen_prom, 1))

# ------------------------------------------------------------------ E · relaciones
H("E · RELACIONES")
corr_us = vs["unidades_vendidas"].corr(vs["stock_disponible"])
P(f"  corr unidades vs stock: {corr_us:.2f}")
ag = mens.copy()
ag["c_mes"] = ag["stock"] / ag["uds"]
ag["c_3"] = ag["stock"] / ag["uds"].rolling(3).mean()
ag["c_12"] = ag["stock"] / ag["uds"].rolling(12).mean()
d_pos = vs.sort_values(["id_tienda", "id_producto", "fecha_mes"]).copy()
d_pos["u12"] = d_pos.groupby(["id_tienda", "id_producto"])["unidades_vendidas"].transform(lambda x: x.rolling(12, min_periods=1).mean())
d_pos = d_pos[(d_pos["stock_disponible"] > 0) & (d_pos["u12"] > 0)]
d_pos["cob"] = d_pos["stock_disponible"] / d_pos["u12"]
med_pos = d_pos.groupby("fecha_mes")["cob"].median()
p90 = d_pos.groupby("fecha_mes")["cob"].quantile(.9); p99 = d_pos.groupby("fecha_mes")["cob"].quantile(.99)
for m in ["2023-01-01", "2025-12-01", "2026-08-01"]:
    P(f"  cobertura {m[:7]}: mes {ag.loc[m,'c_mes']:.2f} · 3m {ag.loc[m,'c_3']:.2f} · 12m {ag.loc[m,'c_12']:.2f} · mediana pos {med_pos[m]:.2f} · p90 {p90[m]:.1f} · p99 {p99[m]:.1f}")
pre = raw["Presupuesto_Ventas_Tienda_Categoria"].copy(); pre["fecha_mes"] = pd.to_datetime(pre["fecha_mes"])
real = ven.groupby(["fecha_mes", "id_tienda", "categoria"])["venta_neta"].sum().reset_index()
pr = pre.merge(real, on=["fecha_mes", "id_tienda", "categoria"], how="left").fillna({"venta_neta": 0})
prv = pr[pr["presupuesto_venta_ars"] > 0]                       # H9: ceros y negativos fuera
cum_y = prv.groupby(prv["fecha_mes"].dt.year).apply(lambda x: x.venta_neta.sum() / x.presupuesto_venta_ars.sum() * 100)
cum_c = prv.groupby("categoria").apply(lambda x: x.venta_neta.sum() / x.presupuesto_venta_ars.sum() * 100)
cum_t = prv.groupby("id_tienda").apply(lambda x: x.venta_neta.sum() / x.presupuesto_venta_ars.sum() * 100)
P("  cumplimiento por año:", cum_y.round(1).to_dict(), f"| cat {cum_c.min():.1f}-{cum_c.max():.1f} | tienda {cum_t.min():.1f}-{cum_t.max():.1f}")
dv = raw["Devoluciones_SKU"]; dv_m = dv.groupby("motivo")["unidades_devueltas"].sum().sort_values(ascending=False)
uds_2225 = ven[ven["fecha_mes"] <= "2025-12-01"]["unidades_vendidas"].sum() + dv["unidades_devueltas"].sum()
P(f"  devoluciones: {len(dv):,} · {dv['unidades_devueltas'].sum():,} uds · tasa {dv['unidades_devueltas'].sum()/uds_2225:.2%} · {dv_m.to_dict()}")
oc = raw["Ordenes_Compra"].copy()
oc["lt"] = (pd.to_datetime(oc["fecha_recepcion"]) - pd.to_datetime(oc["fecha_pedido"])).dt.days
oc = oc.merge(prov[["proveedor", "lead_time_dias", "pedido_minimo_unidades"]], on="proveedor")
oc["dif"] = oc["lt"] - oc["lead_time_dias"]
lt = oc.groupby("proveedor").agg(real=("lt", "mean"), declarado=("lead_time_dias", "first"))
P(f"  lead time real - declarado: media {oc['dif'].mean():.1f} · rango {oc['dif'].min()} a {oc['dif'].max()} · bajo minimo {(oc.unidades < oc.pedido_minimo_unidades).sum()}")
OUT["rel"] = dict(corr_us=round(corr_us, 2), cob={m[:7]: dict(mes=round(ag.loc[m, 'c_mes'], 2), m3=round(ag.loc[m, 'c_3'], 2),
                  m12=round(ag.loc[m, 'c_12'], 2), med=round(med_pos[m], 2), p90=round(p90[m], 1), p99=round(p99[m], 1))
                  for m in ["2023-01-01", "2025-12-01", "2026-08-01"]},
                  cum_y={int(k): round(v, 1) for k, v in cum_y.items()}, cum_c=(round(cum_c.min(), 1), round(cum_c.max(), 1)),
                  cum_t=(round(cum_t.min(), 1), round(cum_t.max(), 1)), dev_n=len(dv), dev_u=int(dv["unidades_devueltas"].sum()),
                  dev_tasa=round(dv["unidades_devueltas"].sum() / uds_2225 * 100, 2), dev_m={k: int(v) for k, v in dv_m.items()},
                  lt_media=round(oc["dif"].mean(), 1), lt_min=int(oc["dif"].min()), lt_max=int(oc["dif"].max()))
json.dump(OUT, open(os.path.join(RES, "eda_ago26.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)

# ------------------------------------------------------------------ GRAFICOS
C1, C2, C3, GR, INK, MUT, GRID = "#3E6FA8", "#E8590C", "#0CA678", "#9A9AA0", "#1C1C1E", "#6E6E73", "#E8EDF3"
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 9.5, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#CBD5E1", "axes.labelcolor": MUT, "xtick.color": MUT, "ytick.color": MUT,
                     "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlecolor": INK,
                     "axes.grid": True, "grid.color": GRID, "axes.axisbelow": True, "legend.frameon": False})
def save(fig, n): fig.tight_layout(); fig.savefig(os.path.join(GRA, n), dpi=160); plt.close(fig); P("  ->", n)
def sombra26(ax):
    ax.axvspan(pd.Timestamp("2026-01-01"), ULT + pd.offsets.MonthEnd(0), color="#FFC72C", alpha=.12, lw=0)
    ax.text(pd.Timestamp("2026-01-15"), ax.get_ylim()[1] * .97, "2026", color=MUT, fontsize=8.5, va="top")

H("GRAFICOS")
fig, ax = plt.subplots(figsize=(10, 4.2)); ax2 = ax.twinx()
ax.plot(mens.index, mens["venta"] / M, color=C1, lw=2, label="Venta neta ($ M)")
ax2.plot(mens.index, mens["uds"] / 1e3, color=C2, lw=1.6, ls="--", label="Unidades (miles)")
ax2.spines["right"].set_visible(True); ax2.grid(False)
ax.set_title("G1 · Venta neta y unidades por mes (ene-2022 a ago-2026)"); sombra26(ax)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="upper left")
save(fig, "G01_venta_mensual.png")

samp = vs[vs["fecha_mes"] > ULT - pd.DateOffset(months=12)]
fig, ax = plt.subplots(figsize=(7, 5))
hb = ax.hexbin(samp["stock_disponible"], samp["unidades_vendidas"], gridsize=40, bins="log", cmap="Blues", mincnt=1)
ax.set_xlabel("Stock disponible (uds)"); ax.set_ylabel("Unidades vendidas en el mes"); fig.colorbar(hb, label="filas (log)")
ax.set_title(f"G2 · Unidades vendidas vs stock por posición (sep-25 a ago-26) · r = {corr_us:.2f}"); save(fig, "G02_unidades_vs_stock.png")

fig, ax = plt.subplots(figsize=(10, 4.2)); a = ag.loc["2023":]
ax.plot(a.index, a["c_mes"], color=C1, label="stock / unidades del mes"); ax.plot(a.index, a["c_3"], color=C3, label="stock / prom. 3 meses")
ax.plot(a.index, a["c_12"], color=C2, label="stock / prom. 12 meses (TP1)"); ax.plot(med_pos.loc["2023":].index, med_pos.loc["2023":], color=GR, ls="--", label="mediana por posición")
ax.set_ylabel("meses de stock"); ax.set_title("G3 · Cobertura de inventario según la definición de cálculo"); sombra26(ax); ax.legend(ncol=2)
save(fig, "G03_cobertura.png")

fig, ax = plt.subplots(figsize=(9, 4)); x = np.arange(1, 13); w = .38
ax.bar(x - w / 2, idx_naive.reindex(x), w, color=GR, label="100 = promedio de cada año (TP1)")
ax.bar(x + w / 2, idx_adj.reindex(x), w, color=C1, label="100 = tendencia (media móvil 12 m)")
ax.axhline(100, color=INK, lw=.8); ax.set_xticks(x, ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
ax.set_title("G4 · Índice estacional de la venta, antes y después de ajustar por tendencia"); ax.legend(); save(fig, "G04_estacionalidad.png")

fig, ax = plt.subplots(figsize=(9, 4.2)); y = np.arange(len(bycat))
ax.barh(y + .2, bycat["pct"], .4, color=C1, label="% de la venta"); ax.barh(y - .2, bycat["pct_sku"], .4, color=GR, label="% de los SKUs")
for i, (p, mg) in enumerate(zip(bycat["pct"], bycat["margen"])): ax.text(p + .3, i + .2, f"{p:.1f}% · margen {mg:.1f}%", va="center", fontsize=8, color=MUT)
ax.set_yticks(y, bycat.index); ax.invert_yaxis(); ax.set_title("G5 · Participación en la venta vs en el catálogo, por categoría"); ax.legend(loc="lower right")
save(fig, "G05_categorias.png")

fig, ax = plt.subplots(figsize=(8, 3.6)); r = byreg.sort_values()
ax.barh(r.index, r.values, color=C1)
for i, (k, v) in enumerate(r.items()): ax.text(v + .4, i, f"{v:.1f}% · {ntie[k]} tiendas ({ntie[k]/28*100:.0f}% de la red)", va="center", fontsize=8.5, color=MUT)
ax.set_xlim(0, r.max() * 1.45); ax.set_title("G6 · Venta por región frente a su peso en la red de tiendas"); save(fig, "G06_region.png")

fig, ax = plt.subplots(figsize=(7.5, 4.5)); xs = np.arange(1, len(cum) + 1) / len(cum) * 100
ax.plot(xs, cum.values * 100, color=C1, lw=2); ax.axhline(80, color=GR, ls="--", lw=1); ax.axvline(n80 / len(cum) * 100, color=GR, ls="--", lw=1)
ax.annotate(f"{n80} SKUs ({n80/len(cum):.0%}) = 80% de la venta", (n80 / len(cum) * 100, 80), xytext=(40, 55), color=INK,
            arrowprops=dict(arrowstyle="->", color=MUT))
ax.set_xlabel("% de SKUs (ordenados por venta)"); ax.set_ylabel("% de venta acumulada"); ax.set_title("G7 · Concentración de la venta por SKU (Pareto)")
save(fig, "G07_pareto.png")

fig, ax = plt.subplots(figsize=(8, 4.5)); cols = {"Grande": C1, "Mediano": C3, "Chico": C2}
for f, g in bt.groupby("formato"): ax.scatter(g["m2_venta"], g["venta"], s=45, color=cols.get(f, GR), label=f, alpha=.85)
for t_, rr in bt.iterrows(): ax.annotate(t_, (rr["m2_venta"], rr["venta"]), fontsize=7, color=MUT, xytext=(3, 2), textcoords="offset points")
ax.set_xlabel("m² de venta"); ax.set_ylabel("Venta ene-22 a ago-26 ($ M)"); ax.legend(title="Formato")
ax.set_title(f"G8 · Venta por tienda vs superficie · r = {corr_m2:.2f}"); save(fig, "G08_tiendas.png")

pm = prv.groupby("fecha_mes")[["presupuesto_venta_ars", "venta_neta"]].sum() / M
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(pm.index, pm["presupuesto_venta_ars"], color=GR, lw=2, label="Presupuesto"); ax.plot(pm.index, pm["venta_neta"], color=C1, lw=2, label="Venta real")
ax2 = ax.twinx(); ax2.plot(pm.index, pm["venta_neta"] / pm["presupuesto_venta_ars"] * 100, color=C2, lw=1, ls=":", label="Cumplimiento %")
ax2.set_ylim(80, 100); ax2.spines["right"].set_visible(True); ax2.grid(False); ax2.set_ylabel("cumplimiento %")
ax.set_ylabel("$ M"); ax.set_title("G9 · Presupuesto vs venta real (sin celdas inválidas, H9)"); sombra26(ax)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="upper left")
save(fig, "G09_presupuesto.png")

fig, ax = plt.subplots(figsize=(8, 3.6)); dm = dv_m.sort_values()
colores = [C2 if "rotacion" in k.lower() else C1 for k in dm.index]
ax.barh(dm.index, dm.values, color=colores)
for i, v in enumerate(dm.values): ax.text(v + 20, i, f"{v:,} uds".replace(",", "."), va="center", fontsize=8.5, color=MUT)
ax.set_xlim(0, dm.max() * 1.2); ax.set_title("G10 · Devoluciones por motivo (uds, 2022-2025) · naranja = devolución a proveedor")
save(fig, "G10_devoluciones.png")

fig, ax = plt.subplots(figsize=(8, 4)); lt = lt.sort_values("declarado"); y = np.arange(len(lt))
ax.barh(y - .2, lt["declarado"], .4, color=GR, label="Declarado (Proveedores)"); ax.barh(y + .2, lt["real"], .4, color=C1, label="Real (OC)")
ax.set_yticks(y, lt.index); ax.set_xlabel("días"); ax.legend(loc="lower right")
ax.set_title(f"G11 · Lead time real vs declarado · diferencia media {oc['dif'].mean():+.1f} días"); save(fig, "G11_leadtime.png")

fig, axs = plt.subplots(1, 3, figsize=(12, 3.6))
pos12 = u12m[u12m["unidades_vendidas"] > 0]
axs[0].hist(pos12["unidades_vendidas"].clip(upper=pos12["unidades_vendidas"].quantile(.99)), bins=30, color=C1); axs[0].set_title("Unidades por posición-mes (>0)")
axs[1].hist((pos12["venta_neta"] / 1e3).clip(upper=pos12["venta_neta"].quantile(.99) / 1e3), bins=30, color=C1); axs[1].set_title("Venta por posición-mes ($ miles)")
axs[2].hist(s_pos["stock_disponible"].clip(upper=s_pos["stock_disponible"].quantile(.99)), bins=30, color=C1); axs[2].set_title("Stock por posición, ago-26")
fig.suptitle("G12 · Distribuciones por posición (sep-25 a ago-26, recortadas en p99)", x=.01, ha="left", fontweight="bold", color=INK)
save(fig, "G12_distribuciones.png")
LOG.close()
