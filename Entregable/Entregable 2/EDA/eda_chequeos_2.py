"""Chequeos de segunda vuelta sobre discrepancias detectadas en eda.py."""
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(BASE, "..", "..", "..", "Datasets"))
LOG = open(os.path.join(BASE, "resultados", "eda_chequeos_2_log.txt"), "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n")
rd = lambda n: pd.read_csv(os.path.join(DATA, n + ".csv"))
K = ["fecha_mes", "id_tienda", "id_producto"]
CAT_MAP = {"Decoración": "Decoracion", "DECO": "Decoracion", "Textil Hogar": "Textil hogar", "TEXTIL_HOGAR": "Textil hogar"}

v = rd("Ventas_SKU_tienda_mensual").drop_duplicates(K); s = rd("Stock_SKU_tienda_mensual").drop_duplicates(K)
v[["unidades_vendidas", "venta_neta"]] = v[["unidades_vendidas", "venta_neta"]].clip(lower=0)
s["stock_disponible"] = s["stock_disponible"].clip(lower=0)
v["fecha_mes"] = pd.to_datetime(v["fecha_mes"]); s["fecha_mes"] = pd.to_datetime(s["fecha_mes"])
cat = rd("Productos_catalogo"); cat["categoria"] = cat["categoria"].replace(CAT_MAP); cat = cat.drop_duplicates("id_producto")
tiendas = rd("Tiendas")

P("== A. Liquidaciones: las 8 fechas 'no parseables'")
l = rd("Liquidaciones")
for col in ["fecha_inicio", "fecha_fin"]:
    odd = l[~l[col].astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}")]
    P(f"  {col}: {len(odd)} filas con formato distinto a AAAA-MM-DD -> {odd[col].tolist()}")
P("  Parseadas con formato libre: fin<inicio =", int((pd.to_datetime(l['fecha_fin'], format='mixed') < pd.to_datetime(l['fecha_inicio'], format='mixed')).sum()))

P("\n== B. Stock total y cobertura con distintas definiciones")
st = s.groupby("fecha_mes")["stock_disponible"].sum(); un = v.groupby("fecha_mes")["unidades_vendidas"].sum()
yr = pd.DataFrame({"stock_total_prom_mes": st.groupby(st.index.year).mean(), "stock_dic": st[st.index.month == 12].groupby(st[st.index.month == 12].index.year).sum(),
                   "unidades_anio": un.groupby(un.index.year).sum()})
P(yr.round(0).to_string())
P(f"  Ratios 2025/2023: stock total prom mensual={yr.loc[2025,'stock_total_prom_mes']/yr.loc[2023,'stock_total_prom_mes']:.2f} | stock dic={yr.loc[2025,'stock_dic']/yr.loc[2023,'stock_dic']:.2f} | unidades={yr.loc[2025,'unidades_anio']/yr.loc[2023,'unidades_anio']:.2f}")
vt = v.groupby("fecha_mes")["venta_neta"].sum()
P(f"  Ratio venta $ 2025/2023={vt['2025'].sum()/vt['2023'].sum():.2f}")
cov1 = st / un
cov12 = st / un.rolling(12).mean()
cov3 = st / un.rolling(3).mean()
for lab, ser in [("stock/unidades del mes", cov1), ("stock/prom 3m", cov3), ("stock/prom 12m", cov12)]:
    P(f"  Cobertura {lab}: ene-23={ser['2023-01-01']:.2f} dic-23={ser['2023-12-01']:.2f} dic-25={ser['2025-12-01']:.2f} prom2023={ser['2023'].mean():.2f} prom2025={ser['2025'].mean():.2f}")
# cobertura por posición (mediana)
j = s.merge(v, on=K)
j = j.sort_values(K)
j["u12"] = j.groupby(["id_tienda", "id_producto"])["unidades_vendidas"].transform(lambda x: x.rolling(12, min_periods=1).mean())
jj = j[(j["stock_disponible"] > 0) & (j["u12"] > 0)].copy(); jj["cov"] = jj["stock_disponible"] / jj["u12"]
med = jj.groupby("fecha_mes")["cov"].median(); p90 = jj.groupby("fecha_mes")["cov"].quantile(.9)
P(f"  Cobertura por posición (stock / prom venta hasta 12m) mediana: ene-23={med['2023-01-01']:.2f} dic-25={med['2025-12-01']:.2f} | p90 ene-23={p90['2023-01-01']:.2f} dic-25={p90['2025-12-01']:.2f}")

P("\n== C. Estacionalidad: ¿es estacionalidad o crecimiento?")
m = v.groupby("fecha_mes").agg(venta=("venta_neta", "sum"), unidades=("unidades_vendidas", "sum"))
m["mm12c"] = m["unidades"].rolling(12, center=True).mean()
m["ratio_tendencia"] = m["unidades"] / m["mm12c"] * 100
P("  Unidades / media móvil centrada 12m (x100), promedio por mes calendario: " + str(m["ratio_tendencia"].groupby(m.index.month).mean().round(0).to_dict()))
P("  Unidades por mes 2023: " + str(m.loc["2023", "unidades"].tolist()))
P("  Unidades por mes 2024: " + str(m.loc["2024", "unidades"].tolist()))
P("  Unidades por mes 2025: " + str(m.loc["2025", "unidades"].tolist()))
pos = v.groupby("fecha_mes").size()
m["unid_por_posicion"] = m["unidades"] / pos
P("  Unidades por posición SKU-tienda por mes 2025: " + str(m.loc["2025", "unid_por_posicion"].round(2).tolist()))
P("  Unidades por posición promedio por mes calendario 2023-2025: " + str(m.loc["2023":"2025", "unid_por_posicion"].groupby(m.loc["2023":"2025"].index.month).mean().round(2).to_dict()))
P("  Posiciones (filas) por mes, cada 6 meses: " + str(pos.iloc[::6].to_dict()))
yoy = m["unidades"].pct_change(12) * 100
P("  Variación interanual de unidades 2025 por mes (%): " + str(yoy["2025"].round(1).tolist()))
# por evento
cal = rd("Calendario"); cal["fecha"] = pd.to_datetime(cal["fecha"])
P("  (Granularidad mensual: Hot Sale 15-17 jun, Black Friday 24-25 nov, Navidad 15-31 dic no son aislables día a día)")
for c_ in sorted(cat["categoria"].unique()):
    vc = v[v["id_producto"].map(cat.set_index("id_producto")["categoria"]) == c_].groupby("fecha_mes")["unidades_vendidas"].sum()
    r = (vc / vc.rolling(12, center=True).mean() * 100)
    P(f"   {c_}: índice sobre tendencia ene={r[r.index.month==1].mean():.0f} jun={r[r.index.month==6].mean():.0f} nov={r[r.index.month==11].mean():.0f} dic={r[r.index.month==12].mean():.0f} (rango {r.groupby(r.index.month).mean().min():.0f}-{r.groupby(r.index.month).mean().max():.0f})")

P("\n== D. Ventas antes de la apertura de la tienda")
t = tiendas.set_index("id_tienda")
first = v[v["unidades_vendidas"] > 0].groupby("id_tienda")["fecha_mes"].min()
tt = t[["nombre_tienda", "fecha_apertura"]].join(first.rename("primer_mes_con_venta"))
tt["fecha_apertura"] = pd.to_datetime(tt["fecha_apertura"])
tt["meses_vendiendo_antes_apertura"] = ((tt["fecha_apertura"].dt.to_period("M") - tt["primer_mes_con_venta"].dt.to_period("M")).apply(lambda x: x.n)).clip(lower=0)
pre = v.merge(t[["fecha_apertura"]], left_on="id_tienda", right_index=True)
pre = pre[pre["fecha_mes"] < pd.to_datetime(pre["fecha_apertura"]).dt.to_period("M").dt.to_timestamp()]
tt["venta_M_antes_apertura"] = (pre.groupby("id_tienda")["venta_neta"].sum() / 1e6).round(1)
P(tt[tt["meses_vendiendo_antes_apertura"] > 0].to_string())
P(f"  Total filas antes de apertura: {len(pre):,} | venta ${pre['venta_neta'].sum()/1e6:,.1f} M | unidades {pre['unidades_vendidas'].sum():,}")
P(f"  Primer mes con venta por tienda (todas): {first.dt.strftime('%Y-%m').value_counts().sort_index().to_dict()}")

P("\n== E. Presupuesto: ceros, negativos y celdas sin venta real (2022-2025)")
pr = rd("Presupuesto_Ventas_Tienda_Categoria")
P("  Negativos: \n" + pr[pr["presupuesto_venta_ars"] < 0].to_string())
z = pr[pr["presupuesto_venta_ars"] == 0]
P(f"  Ceros por mes: {z['fecha_mes'].value_counts().sort_index().to_dict()}")
P(f"  Ceros por tienda: {z['id_tienda'].value_counts().to_dict()}")
v["categoria"] = v["id_producto"].map(cat.set_index("id_producto")["categoria"])
rc = v.groupby([v["fecha_mes"].dt.strftime("%Y-%m-%d"), "id_tienda", "categoria"])["venta_neta"].sum().rename("real")
pv = pr.set_index(["fecha_mes", "id_tienda", "categoria"]).join(rc, how="left")
pv = pv[pv.index.get_level_values(0) <= "2025-12-01"]
P(f"  2022-2025: celdas presupuesto sin fila de venta={int(pv['real'].isna().sum())} | de ellas con presupuesto>0: {int(((pv['real'].isna()) & (pv['presupuesto_venta_ars']>0)).sum())}")
P(f"  2022-2025: celdas con presupuesto 0 o negativo y venta real>0: {int(((pv['presupuesto_venta_ars']<=0) & (pv['real']>0)).sum())}")
pvc = pv.groupby(level=2)[["presupuesto_venta_ars", "real"]].sum(); pvc["cumpl_%"] = pvc["real"] / pvc["presupuesto_venta_ars"] * 100
P("  Cumplimiento por categoría 2022-2025: " + str(pvc["cumpl_%"].round(1).to_dict()))
pvt = pv.groupby(level=1)[["presupuesto_venta_ars", "real"]].sum(); pvt["cumpl_%"] = pvt["real"] / pvt["presupuesto_venta_ars"] * 100
P("  Cumplimiento por tienda 2022-2025 (min/max): " + str(pvt["cumpl_%"].describe().round(1).to_dict()))
cell = pv.dropna(); cell = cell[cell["presupuesto_venta_ars"] > 0]; cr = cell["real"] / cell["presupuesto_venta_ars"] * 100
P("  Cumplimiento por celda mes-tienda-categoría: " + str(cr.describe(percentiles=[.05, .25, .5, .75, .95]).round(1).to_dict()))

P("\n== F. Precio implícito vs precio de lista VIGENTE en ese mes (Historial_Precios)")
hp = rd("Historial_Precios_SKU"); hp["d"] = pd.to_datetime(hp["fecha_vigencia_desde"]); hp["h"] = pd.to_datetime(hp["fecha_vigencia_hasta"]).fillna(pd.Timestamp("2099-01-01"))
vp = v[(v["unidades_vendidas"] > 0)].copy(); vp["mid"] = vp["fecha_mes"] + pd.Timedelta(days=14)
vp = vp.merge(hp[["id_producto", "d", "h", "precio_lista"]], on="id_producto")
vp = vp[(vp["mid"] >= vp["d"]) & (vp["mid"] <= vp["h"])]
vp["ratio"] = vp["venta_neta"] / vp["unidades_vendidas"] / vp["precio_lista"]
P(f"  Filas emparejadas: {len(vp):,} | ratio precio implícito / lista vigente: {vp['ratio'].describe(percentiles=[.01,.05,.5,.95,.99]).round(3).to_dict()}")
P(f"  ratio > 1.0: {(vp['ratio']>1.0001).mean():.2%} | ratio > 1.5: {(vp['ratio']>1.5).mean():.2%} | ratio < 0.5: {(vp['ratio']<0.5).mean():.2%}")
cp = hp.sort_values(["id_producto", "d"]); cp["var"] = cp.groupby("id_producto")["precio_lista"].pct_change() * 100
P(f"  Variación de precio entre vigencias consecutivas (%): {cp['var'].describe(percentiles=[.05,.5,.95]).round(1).to_dict()}")
P(f"  Ejemplo SKU00001: " + hp[hp['id_producto']=='SKU00001'][['fecha_vigencia_desde','fecha_vigencia_hasta','precio_lista','costo_unitario']].to_string())
P(f"  Historial: vigencias con 'desde' > 2025-12-31: {int((hp['d']>'2025-12-31').sum())} | costo nulo en historial: {int(hp['costo_unitario'].isna().sum())} (SKUs {hp.loc[hp['costo_unitario'].isna(),'id_producto'].nunique()})")

P("\n== G. Stock en tránsito vs Transferencias")
tr = rd("Transferencias_Stock"); tr["e"] = pd.to_datetime(tr["fecha_envio"]); tr["r"] = pd.to_datetime(tr["fecha_recepcion"])
months = pd.date_range("2022-01-01", "2025-12-01", freq="MS")
rows = []
for mo in months:
    eom = mo + pd.offsets.MonthEnd(0)
    intr = tr[(tr["e"] <= eom) & (tr["r"] > eom) & (tr["destino"] != "DEP-CENTRAL")]["unidades"].sum()
    rows.append((mo, intr))
itr = pd.Series(dict(rows))
sit = s.groupby("fecha_mes")["stock_en_transito"].sum()
P(f"  Unidades en tránsito a fin de mes según Transferencias (hacia tiendas) vs suma stock_en_transito: corr={itr.corr(sit):.3f} | dic-25: {itr['2025-12-01']:,} vs {sit['2025-12-01']:,} | prom: {itr.mean():,.0f} vs {sit.mean():,.0f}")
P(f"  Transferencias con SKU/tienda destino sin fila de stock ese mes: " +
  str(int((~tr.assign(fecha_mes=tr['e'].dt.to_period('M').dt.to_timestamp()).rename(columns={'destino':'id_tienda'}).merge(s[K], on=K, how='left', indicator=True)['_merge'].eq('both')).sum())) + f" de {len(tr)}")

P("\n== H. Liquidaciones 'Discontinuacion' de SKUs Activos")
l["fi"] = pd.to_datetime(l["fecha_inicio"], format="mixed")
ld = l[l["motivo"] == "Discontinuacion"].merge(cat[["id_producto", "estado", "fecha_baja_catalogo"]], on="id_producto")
P(f"  {len(ld)} liquidaciones por discontinuación: SKU Activo={int((ld['estado']=='Activo').sum())} | Discontinuado={int((ld['estado']!='Activo').sum())}")
ldd = ld[ld["estado"] != "Activo"]
P(f"  De las de SKU discontinuado, inicio antes de la baja: {int((ldd['fi'] < pd.to_datetime(ldd['fecha_baja_catalogo'])).sum())}")
P(f"  Liquidaciones sobre SKU+tienda sin stock ese mes: " +
  str(int((~l[l['tienda']!='Todas'].assign(fecha_mes=l['fi'].dt.to_period('M').dt.to_timestamp()).rename(columns={'tienda':'id_tienda'}).merge(s[s['stock_disponible']>0][K], on=K, how='left', indicator=True)['_merge'].eq('both')).sum())) + f" de {int((l['tienda']!='Todas').sum())}")

P("\n== I. Promociones: duplicados, fechas invertidas y fuera de evento")
pm = rd("Promociones_Comerciales")
P("  Duplicados por id: \n" + pm[pm.duplicated("id_promocion", keep=False)].to_string())
P("  Fin < inicio: \n" + pm[pd.to_datetime(pm["fecha_fin"]) < pd.to_datetime(pm["fecha_inicio"])].to_string())
P("  Descuento fuera de rango: \n" + pm[(pm["descuento_pct"] < 0) | (pm["descuento_pct"] > 100)].to_string())
bad = []
for _, r in pm.dropna(subset=["evento_asociado"]).iterrows():
    dd = cal[(cal["fecha"] >= r["fecha_inicio"]) & (cal["fecha"] <= r["fecha_fin"])]
    if r["evento_asociado"] not in set(dd["evento_especial"].dropna()): bad.append(r)
P("  Promos cuyo evento no cae en sus fechas: \n" + pd.DataFrame(bad).to_string())

P("\n== J. Horizonte temporal por fuente (fin de datos)")
for n, cols in [("Ventas_SKU_tienda_mensual", ["fecha_mes"]), ("Stock_SKU_tienda_mensual", ["fecha_mes"]), ("Stock_Deposito_Central", ["fecha_mes"]),
                ("Presupuesto_Ventas_Tienda_Categoria", ["fecha_mes"]), ("Ordenes_Compra", ["fecha_pedido", "fecha_recepcion"]),
                ("Transferencias_Stock", ["fecha_envio", "fecha_recepcion"]), ("Historial_Precios_SKU", ["fecha_vigencia_desde"]),
                ("Promociones_Comerciales", ["fecha_inicio"]), ("Liquidaciones", ["fecha_inicio"]), ("Devoluciones_SKU", ["fecha"]), ("Calendario", ["fecha"])]:
    df = rd(n)
    for c_ in cols:
        d = pd.to_datetime(df[c_], format="mixed", errors="coerce")
        P(f"  {n}.{c_}: {d.min().date()} -> {d.max().date()} | registros posteriores a 2025-12-31: {int((d > '2025-12-31').sum())}")
LOG.close()
