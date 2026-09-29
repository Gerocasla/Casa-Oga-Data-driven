# -*- coding: utf-8 -*-
import os, json, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding="utf-8")
E2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img"); os.makedirs(OUT, exist_ok=True)
L = lambda p: json.load(open(p, encoding="utf-8"))
I = L(os.path.join(E2, "Modelo", "resultados", "insights.json"))
E = L(os.path.join(E2, "EDA", "resultados", "eda_ago26.json"))
A = L(os.path.join(E2, "EDA", "resultados", "antes_despues.json"))
BG, INK, MUT, GRID = "#FBFBF8", "#14213D", "#5B6475", "#E4E7EC"
BLUE, ORANGE, GREEN, GREY, GOLD = "#3E6FA8", "#E8590C", "#0CA678", "#A1A1AA", "#F5B800"
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 20, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#C9CED6", "axes.labelcolor": MUT, "xtick.color": MUT, "ytick.color": MUT,
                     "axes.grid": True, "grid.color": GRID, "axes.axisbelow": True, "legend.frameon": False,
                     "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG})
def save(fig, n): fig.tight_layout(); fig.savefig(os.path.join(OUT, n), dpi=100); plt.close(fig); print(n)
def fmt_mes(ax, labels, every=6):
    ax.set_xticks(range(0, len(labels), every)); ax.set_xticklabels([labels[i] for i in range(0, len(labels), every)])

# 1 venta mensual bruta/neta desde las series (eda no guarda la serie: recalculo liviano)
D = os.path.join(os.path.dirname(os.path.dirname(E2)), "Datasets_Normalizados")
K = ["fecha_mes", "id_tienda", "id_producto"]
v = pd.read_csv(os.path.join(D, "Ventas_SKU_tienda_mensual.csv"))
pos = v[v.unidades_vendidas >= 0].drop_duplicates(K); neg = v[v.unidades_vendidas < 0]
vn = pd.concat([pos, neg]).groupby(K, as_index=False)[["unidades_vendidas", "venta_neta"]].sum()
m = vn.groupby("fecha_mes").agg(venta=("venta_neta", "sum"), pos=("venta_neta", "size"), uds=("unidades_vendidas", "sum"))
m.index = pd.to_datetime(m.index)
fig, ax = plt.subplots(figsize=(16, 7.4))
ax.plot(m.index, m.venta / 1e6, color=BLUE, lw=3.5)
ax.axvspan(pd.Timestamp("2026-01-01"), pd.Timestamp("2026-08-31"), color=GOLD, alpha=.14, lw=0)
ax.set_ylabel("$ M por mes"); ax.set_ylim(0)
ax2 = ax.twinx(); ax2.plot(m.index, m.uds / m.pos, color=ORANGE, lw=2.5, ls="--"); ax2.set_ylim(0, 5)
ax2.set_ylabel("unidades por posición", color=ORANGE); ax2.grid(False); ax2.spines["right"].set_visible(True); ax2.tick_params(colors=ORANGE)
ax.text(pd.Timestamp("2026-01-20"), ax.get_ylim()[1] * .93, "2026", color=MUT, fontsize=20)
save(fig, "c01_venta_mensual.png")

# 2 estacionalidad
mm = m.venta.rolling(12, center=True).mean(); adj = (m.venta / mm * 100).dropna(); ia = adj.groupby(adj.index.month).mean()
nv = m.loc["2023":"2025"].copy(); nv["i"] = nv.groupby(nv.index.year).venta.transform(lambda x: x / x.mean() * 100); iv = nv.groupby(nv.index.month).i.mean()
fig, ax = plt.subplots(figsize=(16, 7.4)); x = np.arange(1, 13); w = .38
ax.bar(x - w / 2, iv, w, color=GREY, label="Cálculo del TP1 (100 = promedio de cada año)")
ax.bar(x + w / 2, ia, w, color=BLUE, label="Ajustado por tendencia (media móvil 12 m)")
ax.axhline(100, color=INK, lw=1.2); ax.set_xticks(x, ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"])
ax.set_ylim(0, 130); ax.legend(loc="upper left", ncol=1)
save(fig, "c02_estacionalidad.png")

# 3 cobertura: definiciones
s = pd.read_csv(os.path.join(D, "Stock_SKU_tienda_mensual.csv")).drop_duplicates(K); s["stock_disponible"] = s.stock_disponible.clip(lower=0)
st = s.groupby("fecha_mes").stock_disponible.sum(); st.index = pd.to_datetime(st.index)
c12 = (st / m.uds.rolling(12).mean()).loc["2023":]; cm = (st / m.uds).loc["2023":]
fig, ax = plt.subplots(figsize=(16, 7.4))
ax.plot(c12.index, c12, color=ORANGE, lw=3.5, label="stock / promedio 12 meses (TP1)")
ax.plot(cm.index, cm, color=BLUE, lw=3.5, label="stock / venta del mes")
pp = I["cobertura_pct"]; ax.plot(pd.to_datetime(pp["meses"]), pp["p50"], color=GREY, lw=3, ls="--", label="mediana por posición")
ax.set_ylabel("meses de stock"); ax.set_ylim(0, 12); ax.legend(loc="upper right")
save(fig, "c03_cobertura_def.png")

# 4 venta 2025 vs 2026
vv = I["venta_25_26"]; fig, ax = plt.subplots(figsize=(16, 7.4)); x = np.arange(8)
ax.bar(x - w / 2, vv["v2025"], w, color=GREY, label="2025"); ax.bar(x + w / 2, vv["v2026"], w, color=BLUE, label="2026")
for i, (a, b) in enumerate(zip(vv["v2025"], vv["v2026"])):
    ax.text(i + w / 2, b + 15, f"{(b/a-1)*100:+.0f}%".replace("-", "−"), ha="center", fontsize=18, color=INK)
ax.set_xticks(x, vv["meses"]); ax.set_ylabel("$ M (bruto)"); ax.legend(loc="upper left", ncol=2); ax.set_ylim(0, 1400)
save(fig, "c04_venta_2526.png")

# 5 percentiles de cobertura
fig, ax = plt.subplots(figsize=(16, 7.4)); mes = pd.to_datetime(pp["meses"])
ax.plot(mes, pp["p99"], color=ORANGE, lw=3.5, label="Percentil 99"); ax.plot(mes, pp["p90"], color=BLUE, lw=3.5, label="Percentil 90")
ax.plot(mes, pp["p50"], color=GREY, lw=3.5, label="Mediana")
ax.axvspan(pd.Timestamp("2026-01-01"), pd.Timestamp("2026-08-31"), color=GOLD, alpha=.14, lw=0)
ax.set_ylabel("meses de stock por posición"); ax.legend(loc="upper left"); ax.set_ylim(0)
save(fig, "c05_cola_cobertura.png")

# 6 prevalencia por mes con particion
pv = I["prevalencia_mes"]; col = {"train": BLUE, "validacion": GREEN, "test": ORANGE, "embargo": GREY}
fig, ax = plt.subplots(figsize=(16, 6.8))
ax.bar(range(len(pv["meses"])), pv["tasa"], color=[col[s] for s in pv["split"]], width=.8)
fmt_mes(ax, [x[2:4] + "-" + x[5:] for x in pv["meses"]], 6); ax.set_ylabel("% de positivos")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=BLUE, label="Train"), Patch(color=GREEN, label="Validación"), Patch(color=ORANGE, label="Test"), Patch(color=GREY, label="Embargo")], loc="upper left", ncol=4)
save(fig, "c06_prevalencia.png")

# 7 capacidad
cp = I["capacidad"]["validacion"]; fig, ax = plt.subplots(figsize=(16, 7.4))
ax.axvspan(420, 700, color=GOLD, alpha=.18, lw=0); ax.text(430, 8, "capacidad declarada\n420–700 / mes", color=MUT, fontsize=18)
ct = I["capacidad"].get("test")
if ct is None:   # insights.json guarda solo validacion: el test sale del CSV del chequeo de senal
    ct = pd.read_csv(os.path.join(E2, "Modelo", "resultados", "capacidad_alertas_v3.csv")).query("split == 'test'")
    ct = {"k": ct.alertas_mes.tolist(), "recall_modelo": ct.recall_modelo.tolist(), "recall_regla": ct.recall_regla.tolist()}
ax.plot(cp["k"], cp["recall_modelo"], color=BLUE, lw=4, marker="o", ms=8, label="Modelo · validación 2025")
ax.plot(cp["k"], cp["recall_regla"], color=BLUE, lw=3, ls="--", marker="o", ms=6, alpha=.55, label="Regla · validación 2025")
ax.plot(ct["k"], ct["recall_modelo"], color=ORANGE, lw=4, marker="o", ms=8, label="Modelo · test 2026")
ax.plot(ct["k"], ct["recall_regla"], color=ORANGE, lw=3, ls="--", marker="o", ms=6, alpha=.55, label="Regla · test 2026")
ax.set_xlabel("alertas por mes"); ax.set_ylabel("% de casos capturados"); ax.set_ylim(0, 100); ax.set_xlim(0, 1020); ax.legend(loc="upper left")
save(fig, "c07_capacidad.png")

# 8 senal univariada top 15
sn = pd.DataFrame(I["senal"]).head(15).iloc[::-1]; fig, ax = plt.subplots(figsize=(13, 9.2)); y = np.arange(len(sn))
ax.barh(y + .2, sn.auc_train, .4, color=BLUE, label="Train (2022-24)"); ax.barh(y - .2, sn.auc_test, .4, color=ORANGE, label="Test (2026)")
ax.set_yticks(y, sn.feature, fontsize=17); ax.set_xlim(.5, 1); ax.set_xlabel("AUC de la variable sola (0,5 = no separa)"); ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.0), ncol=2)
save(fig, "c08_senal.png")

# 9 antes/despues: 3 barras pequenas
met = {r["metrica"]: r for r in A["metricas"]}
pares = [("Venta total\n(M$)", "Venta total ene-22 a ago-26 (M$)"), ("Capital dic-25\n(M$)", "Capital inmovilizado en tiendas a dic-25 (M$ a costo)"),
         ("Decoración\n(% venta)", "Participacion de Decoracion en la venta (%)"), ("Prevalencia\ntarget (%)", "Prevalencia del target (cobertura > 12 a 3 meses, %)")]
fig, axs = plt.subplots(1, 4, figsize=(16, 6.4))
for ax, (lab, k) in zip(axs, pares):
    r = met[k]; ax.bar([0, 1], [r["antes"], r["despues"]], color=[GREY, BLUE], width=.7)
    var = (r["despues"] / r["antes"] - 1) * 100
    import math
    dpp = math.floor((r['despues'] - r['antes']) * 10) / 10 if "Decoracion" in k else round(r["despues"], 1) - round(r["antes"], 1)   # igual que el texto: 22,35 - 20,80 -> 1,5; 3,40 - 2,61 -> 3,4 - 2,6 = 0,8
    txt = (f"{dpp:+.1f} pp" if r["fmt"] == "p" else f"{var:+.1f}%").replace(".", ",").replace("-", "−")
    ax.set_title(lab, fontsize=20, color=INK, loc="center"); ax.set_xticks([0, 1], ["Antes", "Después"]); ax.set_yticks([])
    ax.text(.5, max(r["antes"], r["despues"]) * 1.05, txt, ha="center", fontsize=24, color=INK, fontweight="bold")
    ax.set_ylim(0, max(r["antes"], r["despues"]) * 1.2); ax.spines["left"].set_visible(False); ax.grid(False)
save(fig, "c09_antes_despues.png")

# 10 capital en rojo por categoria
rc = I["rojo_ago26_cat"]; acc = {"Decoracion": "Decoración", "Bano": "Baño", "Iluminacion": "Iluminación", "Organizacion": "Organización"}
fig, ax = plt.subplots(figsize=(13, 7.4)); cats = [acc.get(c, c) for c in rc["cat"]][::-1]; val = rc["capital"][::-1]; pc = rc["pct_capital_cat"][::-1]
ax.barh(cats, val, color=BLUE)
for i, (v_, p_) in enumerate(zip(val, pc)): ax.text(v_ + .6, i, f"${v_:.1f} M · {p_:.1f}% del stock".replace(".", ","), va="center", fontsize=17, color=MUT)
ax.set_xlim(0, max(val) * 1.55); ax.set_xlabel("$ M a costo, ago-2026")
save(fig, "c10_capital_rojo.png")

# 11-12 que cambia en 2026 (catalogo y posiciones sin venta). Bruto: 2026 no trae devoluciones.
b = pos.copy(); b["fecha_mes"] = pd.to_datetime(b.fecha_mes); b["y"] = b.fecha_mes.dt.year; b["m"] = b.fecha_mes.dt.month
wb = b[(b.m <= 8) & b.y.isin([2025, 2026])]
act = set(wb[(wb.y == 2026) & (wb.unidades_vendidas > 0)].id_producto)   # SKUs que siguen vendiendo en 2026
cat = pd.read_csv(os.path.join(D, "Productos_catalogo.csv")).drop_duplicates("id_producto")
alta = b[b.unidades_vendidas > 0].groupby("id_producto").fecha_mes.min()
tot = wb.groupby(["m", "y"]).venta_neta.sum().unstack(); sig = wb[wb.id_producto.isin(act)].groupby(["m", "y"]).venta_neta.sum().unstack()
T = tot.sum(); Sg = sig.sum(); baja = T[2025] - Sg[2025]
s["fecha_mes"] = pd.to_datetime(s.fecha_mes); costo = cat.set_index("id_producto").costo_unitario
def sin_venta(fin):   # posiciones de SKUs activos con stock y ninguna unidad vendida en los ultimos 3 meses
    st_ = s[(s.fecha_mes == fin) & s.id_producto.isin(act) & (s.stock_disponible > 0)].set_index(["id_tienda", "id_producto"]).stock_disponible
    u3 = b[(b.fecha_mes > fin - pd.DateOffset(months=3)) & (b.fecha_mes <= fin)].groupby(["id_tienda", "id_producto"]).unidades_vendidas.sum()
    d = st_[u3.reindex(st_.index).fillna(0) <= 0]
    return d, (d * d.index.get_level_values(1).map(costo)).sum() / 1e6
meses_sv = pd.date_range("2024-03-01", b.fecha_mes.max(), freq="MS"); nsv = [len(sin_venta(f)[0]) for f in meses_sv]
d_dic, k_dic = sin_venta(pd.Timestamp("2025-12-01")); d_fin, k_fin = sin_venta(meses_sv[-1])
lq = pd.read_csv(os.path.join(D, "Liquidaciones.csv")); lq["f"] = pd.to_datetime(lq.fecha_inicio); lq8 = lq[lq.f.dt.month <= 8]
liq = lq8.groupby(lq8.f.dt.year).size(); liq_sob = lq8[lq8.motivo == "Sobrestock"].groupby(lq8.f.dt.year).size()
l26 = pd.MultiIndex.from_frame(lq[lq.f.dt.year == 2026][["tienda", "id_producto"]])
oc = pd.read_csv(os.path.join(D, "Ordenes_Compra.csv")); oc["f"] = pd.to_datetime(oc.fecha_pedido)
oc7 = oc[(oc.f.dt.month <= 7) & oc.id_producto.isin(act)].groupby(oc.f.dt.year).unidades.sum()
C26 = {"var_total": (T[2026] / T[2025] - 1) * 100, "var_sigue": (Sg[2026] / Sg[2025] - 1) * 100,
       "var_sigue_mes": ((sig[2026] / sig[2025] - 1) * 100).tolist(), "var_total_mes": ((tot[2026] / tot[2025] - 1) * 100).tolist(),
       "gap_M": (T[2025] - T[2026]) / 1e6, "baja_M": baja / 1e6, "baja_pp": baja / T[2025] * 100,
       "skus_baja": len(set(wb[(wb.y == 2025) & (wb.unidades_vendidas > 0)].id_producto) - act), "skus_sigue": len(act),
       "baja_discontinuados": int(cat[cat.id_producto.isin(set(wb[wb.y == 2025].id_producto) - act)].estado.eq("Discontinuado").sum()),
       "altas_por_anio": alta.dt.year.value_counts().sort_index().to_dict(), "ultima_alta": str(alta.max().date()),
       "sin_venta_dic25": len(d_dic), "sin_venta_fin": len(d_fin), "capital_dic25": k_dic, "capital_fin": k_fin,
       "sin_venta_mes": dict(zip([str(f.date())[:7] for f in meses_sv], nsv)),
       "liq": liq.to_dict(), "liq_sobrestock": liq_sob.to_dict(), "sin_venta_liquidadas_2026": int(d_fin.index.isin(l26).sum()),
       "oc_activos_ene_jul": oc7.to_dict()}
C26 = json.loads(json.dumps(C26, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
json.dump(C26, open(os.path.join(E2, "EDA", "resultados", "cambio_2026.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: v for k, v in C26.items() if not isinstance(v, (list, dict))})

fig, ax = plt.subplots(figsize=(16, 7.4)); x = np.arange(1, 9)
ax.axhline(0, color=INK, lw=1.2)
ax.plot(x, C26["var_total_mes"], color=GREY, lw=3.5, marker="o", ms=9, label="Venta total")
ax.plot(x, C26["var_sigue_mes"], color=BLUE, lw=4, marker="o", ms=9, label=f"Solo los {len(act)} SKUs que siguen")
ax.fill_between(x, C26["var_total_mes"], C26["var_sigue_mes"], color=GREY, alpha=.15, lw=0)
ax.text(2.1, (C26["var_total_mes"][1] + C26["var_sigue_mes"][1]) / 2, "SKUs dados de\nbaja a fin de 2025", color=MUT, fontsize=18, va="center")
for i in (0, 7):
    for serie, c in (("var_total_mes", GREY), ("var_sigue_mes", BLUE)):
        ax.text(x[i] + (.12 if i else -.12), C26[serie][i], f"{C26[serie][i]:+.0f}%".replace("-", "−"), color=c, fontsize=19, fontweight="bold",
                ha="left" if i else "right", va="center")
ax.set_xticks(x, ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago"]); ax.set_xlim(.4, 8.7)
ax.set_ylabel("variación contra el mismo mes de 2025 (%)"); ax.set_ylim(-24, 4); ax.legend(loc="lower right")
save(fig, "c11_caida_catalogo.png")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, 7.4), gridspec_kw={"width_ratios": [2.3, 1]})
a1.plot(meses_sv, nsv, color=ORANGE, lw=4); a1.axvspan(pd.Timestamp("2026-01-01"), meses_sv[-1] + pd.DateOffset(days=30), color=GOLD, alpha=.14, lw=0)
a1.set_ylim(0, max(nsv) * 1.15); a1.set_title("Posiciones con stock y sin venta en 3 meses", fontsize=20, color=INK, loc="left")
a1.set_xticks(pd.to_datetime(["2024-07-01", "2025-01-01", "2025-07-01", "2026-01-01", "2026-07-01"]), ["jul-24", "ene-25", "jul-25", "ene-26", "jul-26"])
yy = [2024, 2025, 2026]; lv = [C26["liq"].get(str(y_), 0) for y_ in yy]
a2.bar(range(3), lv, color=[GREY, GREY, BLUE], width=.65)
for i, v_ in enumerate(lv): a2.text(i, v_ + 3, str(v_), ha="center", fontsize=20, color=INK, fontweight="bold")
a2.set_xticks(range(3), [str(y_) for y_ in yy]); a2.set_yticks([]); a2.spines["left"].set_visible(False); a2.grid(False)
a2.set_ylim(0, max(lv) * 1.2); a2.set_title("Liquidaciones ene-ago", fontsize=20, color=INK, loc="left")
save(fig, "c12_sin_venta_liquidaciones.png")
