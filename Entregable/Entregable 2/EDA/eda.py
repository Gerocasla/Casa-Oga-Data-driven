"""EDA + chequeos de calidad — Casa Óga, Entregable 2.
Lee los 15 CSV de Data-Driven/Datasets, sin modificarlos.
Salidas: EDA/resultados/*.csv, EDA/graficos/*.png, EDA/resultados/eda_log.txt
"""
import os, sys, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(BASE, "..", "..", "..", "Datasets"))
RES = os.path.join(BASE, "resultados"); GRA = os.path.join(BASE, "graficos")
os.makedirs(RES, exist_ok=True); os.makedirs(GRA, exist_ok=True)
LOG = open(os.path.join(RES, "eda_log.txt"), "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n")
def H(t): P("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

CAT_MAP = {"Decoración": "Decoracion", "DECO": "Decoracion", "Textil Hogar": "Textil hogar",
           "TEXTIL_HOGAR": "Textil hogar", "Iluminación": "Iluminacion", "Organización": "Organizacion"}
CATS = ["Baño", "Cocina y mesa", "Decoracion", "Iluminacion", "Muebles", "Organizacion", "Textil hogar"]

raw = {}
for f in sorted(os.listdir(DATA)):
    if f.endswith(".csv"):
        raw[f[:-4]] = pd.read_csv(os.path.join(DATA, f), dtype=str, keep_default_na=True)

# ----------------------------------------------------------------------------------------------
H("1. PERFIL GENERAL Y CALIDAD POR FUENTE (datos crudos)")
KEYS = {"Ventas_SKU_tienda_mensual": ["fecha_mes", "id_tienda", "id_producto"],
        "Stock_SKU_tienda_mensual": ["fecha_mes", "id_tienda", "id_producto"],
        "Stock_Deposito_Central": ["fecha_mes", "id_producto"],
        "Productos_catalogo": ["id_producto"], "Tiendas": ["id_tienda"], "Calendario": ["fecha"],
        "Liquidaciones": ["id_liquidacion"], "Devoluciones_SKU": ["id_devolucion"],
        "Historial_Precios_SKU": ["id_producto", "fecha_vigencia_desde"], "Ordenes_Compra": ["id_oc"],
        "Presupuesto_Ventas_Tienda_Categoria": ["fecha_mes", "id_tienda", "categoria"],
        "Promociones_Comerciales": ["id_promocion"], "Proveedores": ["proveedor"],
        "Transferencias_Stock": ["id_transferencia"], "Costo_almacenamiento": ["categoria"]}
DATECOLS = ["fecha", "fecha_mes", "fecha_alta_catalogo", "fecha_baja_catalogo", "fecha_inicio", "fecha_fin",
            "fecha_vigencia_desde", "fecha_vigencia_hasta", "fecha_pedido", "fecha_recepcion", "fecha_envio",
            "fecha_apertura"]
perfil = []
for name, df in raw.items():
    P(f"\n### {name}: {len(df):,} filas x {df.shape[1]} columnas")
    nulls = df.isna().sum(); nulls = nulls[nulls > 0]
    P("  Nulos:", dict(nulls) if len(nulls) else "ninguno")
    exact = int(df.duplicated().sum())
    k = KEYS.get(name); keydup = int(df.duplicated(subset=k).sum()) if k else None
    P(f"  Duplicados exactos: {exact:,} | Duplicados por clave {k}: {keydup:,}")
    rango = {}
    for c in df.columns:
        if c in DATECOLS:
            d = pd.to_datetime(df[c], errors="coerce", format="%Y-%m-%d")
            bad = int((d.isna() & df[c].notna()).sum())
            rango[c] = (str(d.min().date()) if d.notna().any() else None, str(d.max().date()) if d.notna().any() else None, bad)
            P(f"  Fecha {c}: {rango[c][0]} -> {rango[c][1]} | no parseables: {bad}"
              + (f" ejemplos {df.loc[d.isna() & df[c].notna(), c].unique()[:5].tolist()}" if bad else ""))
    for c in df.columns:
        if c in DATECOLS or c.startswith("id_") or c in ("proveedor",):
            continue
        num = pd.to_numeric(df[c], errors="coerce")
        if num.notna().sum() >= 0.9 * df[c].notna().sum() and df[c].notna().sum() > 0:
            q = num.quantile([0, .01, .05, .25, .5, .75, .95, .99, 1])
            iqr = q[.75] - q[.25]; out = int(((num < q[.25] - 1.5 * iqr) | (num > q[.75] + 1.5 * iqr)).sum())
            P(f"  Num {c}: media={num.mean():,.2f} mediana={q[.5]:,.2f} min={q[0]:,.2f} p1={q[.01]:,.2f} p5={q[.05]:,.2f} "
              f"p25={q[.25]:,.2f} p75={q[.75]:,.2f} p95={q[.95]:,.2f} p99={q[.99]:,.2f} max={q[1]:,.2f} | "
              f"negativos={int((num < 0).sum()):,} ceros={int((num == 0).sum()):,} outliersIQR={out:,} no-numericos={int((num.isna() & df[c].notna()).sum())}")
    perfil.append({"fuente": name, "filas": len(df), "columnas": df.shape[1], "nulos_total": int(df.isna().sum().sum()),
                   "dup_exactos": exact, "dup_clave": keydup, "rangos_fecha": json.dumps(rango, ensure_ascii=False)})
pd.DataFrame(perfil).to_csv(os.path.join(RES, "perfil_fuentes.csv"), index=False, encoding="utf-8-sig")

# ----------------------------------------------------------------------------------------------
H("2. CHEQUEOS ESPECIFICOS DE CALIDAD E INTEGRIDAD REFERENCIAL")
cat_raw = raw["Productos_catalogo"]; tiendas = raw["Tiendas"]
skus_cat = set(cat_raw["id_producto"]); ids_t = set(tiendas["id_tienda"])
for name in ["Ventas_SKU_tienda_mensual", "Stock_SKU_tienda_mensual", "Stock_Deposito_Central", "Liquidaciones",
             "Devoluciones_SKU", "Historial_Precios_SKU", "Ordenes_Compra", "Transferencias_Stock"]:
    df = raw[name]
    P(f"  {name}: SKUs que no existen en catálogo = {len(set(df['id_producto']) - skus_cat)} "
      f"(filas {int((~df['id_producto'].isin(skus_cat)).sum())})")
P(f"  SKUs del catálogo sin ninguna fila de ventas: {len(skus_cat - set(raw['Ventas_SKU_tienda_mensual']['id_producto']))}")
for name, col in [("Ventas_SKU_tienda_mensual", "id_tienda"), ("Stock_SKU_tienda_mensual", "id_tienda"),
                  ("Devoluciones_SKU", "id_tienda"), ("Presupuesto_Ventas_Tienda_Categoria", "id_tienda"),
                  ("Liquidaciones", "tienda"), ("Transferencias_Stock", "origen"), ("Transferencias_Stock", "destino")]:
    v = raw[name][col]; bad = v[~v.isin(ids_t)]
    P(f"  {name}.{col}: valores fuera de Tiendas -> {bad.value_counts().to_dict()}")
for name in ["Productos_catalogo", "Ordenes_Compra"]:
    v = raw[name]["proveedor"]; P(f"  {name}.proveedor fuera de Proveedores.csv: {sorted(set(v) - set(raw['Proveedores']['proveedor']))}")
for name in ["Productos_catalogo", "Presupuesto_Ventas_Tienda_Categoria", "Promociones_Comerciales", "Costo_almacenamiento"]:
    P(f"  {name}.categoria valores: {raw[name]['categoria'].value_counts().to_dict()}")

# catálogo
c = cat_raw.copy()
for col in ["costo_unitario", "precio_lista"]: c[col] = pd.to_numeric(c[col], errors="coerce")
dup_ids = c[c.duplicated("id_producto", keep=False)].sort_values("id_producto")
P(f"\n  Catálogo: {c['id_producto'].nunique()} SKUs únicos en {len(c)} filas. Duplicados: {dup_ids['id_producto'].nunique()} SKUs")
diffcols = {col: int(dup_ids.groupby('id_producto')[col].nunique(dropna=False).gt(1).sum()) for col in c.columns if col != 'id_producto'}
P(f"  Columnas que difieren entre filas duplicadas (n SKUs): {diffcols}")
P(f"  Costo nulo: {int(c['costo_unitario'].isna().sum())} | precio nulo: {int(c['precio_lista'].isna().sum())} | "
  f"precio < costo: {int((c['precio_lista'] < c['costo_unitario']).sum())} | precio == costo: {int((c['precio_lista'] == c['costo_unitario']).sum())}")
alta = pd.to_datetime(c["fecha_alta_catalogo"], errors="coerce"); baja = pd.to_datetime(c["fecha_baja_catalogo"], errors="coerce")
P(f"  Baja < alta: {int((baja < alta).sum())} | Discontinuado sin fecha baja: {int(((c['estado']=='Discontinuado') & baja.isna()).sum())} | "
  f"Activo con fecha baja: {int(((c['estado']=='Activo') & baja.notna()).sum())} | alta > 2025-12-31: {int((alta > '2025-12-31').sum())}")
P(f"  Subcategorías únicas: {c['subcategoria'].nunique()}")
sub_multi = c.assign(cn=c['categoria'].replace(CAT_MAP)).groupby('subcategoria')['cn'].nunique()
P(f"  Subcategorías asignadas a más de 1 categoría (tras normalizar): {sub_multi[sub_multi>1].to_dict()}")

# ventas / stock crudos
v = raw["Ventas_SKU_tienda_mensual"].copy(); s = raw["Stock_SKU_tienda_mensual"].copy()
for col in ["unidades_vendidas", "venta_neta"]: v[col] = pd.to_numeric(v[col], errors="coerce")
for col in ["stock_disponible", "stock_en_transito"]: s[col] = pd.to_numeric(s[col], errors="coerce")
K = ["fecha_mes", "id_tienda", "id_producto"]
for nm, df, vals in [("Ventas", v, ["unidades_vendidas", "venta_neta"]), ("Stock", s, ["stock_disponible", "stock_en_transito"])]:
    kd = df[df.duplicated(K, keep=False)]
    grp = kd.groupby(K)
    n_keys = grp.ngroups; n_extra = int(df.duplicated(K).sum())
    distinct = int(grp[vals].nunique().gt(1).any(axis=1).sum())
    with_zero = int(grp[vals[0]].apply(lambda x: (x == 0).any()).sum())
    P(f"  {nm}: claves duplicadas={n_keys:,} | filas sobrantes={n_extra:,} | claves con valores distintos={distinct:,} | "
      f"claves con algún registro en 0 ({vals[0]})={with_zero:,} | filas por clave max={grp.size().max()} | "
      f"SKUs involucrados={kd['id_producto'].nunique()} (en dup catálogo: {kd['id_producto'].isin(dup_ids['id_producto']).sum()} filas de {len(kd)})")
    P(f"     años de las filas duplicadas: {pd.to_datetime(kd['fecha_mes']).dt.year.value_counts().sort_index().to_dict()}")
neg_v = v[(v["unidades_vendidas"] < 0) | (v["venta_neta"] < 0)]
P(f"  Ventas negativas: filas={len(neg_v):,} | unidades<0={int((v['unidades_vendidas']<0).sum())} venta<0={int((v['venta_neta']<0).sum())} "
  f"| ambas={int(((v['unidades_vendidas']<0)&(v['venta_neta']<0)).sum())} | min unidades={v['unidades_vendidas'].min()} | suma unidades neg={neg_v['unidades_vendidas'].sum():,.0f}")
P(f"  Ventas: unidades=0 y venta!=0: {int(((v['unidades_vendidas']==0)&(v['venta_neta']!=0)).sum())} | unidades>0 y venta<=0: {int(((v['unidades_vendidas']>0)&(v['venta_neta']<=0)).sum())}")
P(f"  Ventas filas con 0 unidades: {int((v['unidades_vendidas']==0).sum()):,} ({(v['unidades_vendidas']==0).mean():.2%})")
P(f"  Stock negativo: filas={int((s['stock_disponible']<0).sum()):,} min={s['stock_disponible'].min()} | transito<0={int((s['stock_en_transito']<0).sum())}")
P(f"  Clave ventas == clave stock (mismas filas): {set(map(tuple, v[K].values)) == set(map(tuple, s[K].values))}")
# grilla
nm_months = v["fecha_mes"].nunique()
P(f"  Meses distintos ventas: {nm_months} ({v['fecha_mes'].min()} a {v['fecha_mes'].max()}); días del mes != 01: {int((~v['fecha_mes'].str.endswith('-01')).sum())}")
# ventas vs apertura tienda
ta = tiendas.set_index("id_tienda")["fecha_apertura"]
vv = v.assign(ap=v["id_tienda"].map(ta))
P(f"  Filas de ventas antes de la apertura de la tienda: {int((pd.to_datetime(vv['fecha_mes']) < pd.to_datetime(vv['ap']).dt.to_period('M').dt.to_timestamp()).sum())}")
P(f"  Tiendas: aperturas {tiendas['fecha_apertura'].min()} a {tiendas['fecha_apertura'].max()}; abiertas después de 2022-01: {tiendas[tiendas['fecha_apertura']>'2022-01-01'][['id_tienda','fecha_apertura']].values.tolist()}")
# ventas fuera de vigencia catálogo
cfirst = c.drop_duplicates("id_producto").set_index("id_producto")
vv = v.assign(alta=v["id_producto"].map(cfirst["fecha_alta_catalogo"]), baja=v["id_producto"].map(cfirst["fecha_baja_catalogo"]))
fm = pd.to_datetime(vv["fecha_mes"]); al = pd.to_datetime(vv["alta"]).dt.to_period("M").dt.to_timestamp(); bj = pd.to_datetime(vv["baja"])
P(f"  Filas de ventas con unidades>0 en meses previos al alta del SKU: {int(((fm < al) & (vv['unidades_vendidas']>0)).sum())} | "
  f"en meses posteriores a la baja: {int(((fm > bj) & (vv['unidades_vendidas']>0)).sum())}")
# precio implícito
vp = v[(v["unidades_vendidas"] > 0) & (v["venta_neta"] > 0)].copy()
vp["precio_impl"] = vp["venta_neta"] / vp["unidades_vendidas"]
vp["precio_lista"] = vp["id_producto"].map(cfirst["precio_lista"].astype(float))
vp["ratio"] = vp["precio_impl"] / vp["precio_lista"]
P(f"  Precio implícito (venta/unidades) / precio_lista del catálogo: {vp['ratio'].describe(percentiles=[.01,.05,.25,.5,.75,.95,.99]).round(3).to_dict()}")
P(f"     ratio > 1.05: {(vp['ratio']>1.05).mean():.2%} | ratio < 0.5: {(vp['ratio']<0.5).mean():.2%}")

# liquidaciones
l = raw["Liquidaciones"].copy(); l["descuento_pct"] = pd.to_numeric(l["descuento_pct"], errors="coerce")
li = pd.to_datetime(l["fecha_inicio"], errors="coerce", format="%Y-%m-%d"); lf = pd.to_datetime(l["fecha_fin"], errors="coerce", format="%Y-%m-%d")
P(f"\n  Liquidaciones: fin<inicio={int((lf<li).sum())} | duración días {(lf-li).dt.days.describe().round(1).to_dict()} | "
  f"descuento fuera [0,100]: {l.loc[(l['descuento_pct']<0)|(l['descuento_pct']>100),'descuento_pct'].tolist()} | tienda='Todas': {int((l['tienda']=='Todas').sum())}")
P(f"  Liquidaciones por año (inicio): {li.dt.year.value_counts().sort_index().to_dict()} | por motivo: {l['motivo'].value_counts().to_dict()}")
ll = l.assign(alta=pd.to_datetime(l["id_producto"].map(cfirst["fecha_alta_catalogo"])), baja=pd.to_datetime(l["id_producto"].map(cfirst["fecha_baja_catalogo"])))
P(f"  Liquidaciones que empiezan antes del alta del SKU: {int((li < ll['alta']).sum())} | motivo Discontinuacion con SKU Activo: "
  f"{int(((l['motivo']=='Discontinuacion') & (l['id_producto'].map(cfirst['estado'])=='Activo')).sum())} de {int((l['motivo']=='Discontinuacion').sum())}")

# devoluciones
d = raw["Devoluciones_SKU"].copy(); d["unidades_devueltas"] = pd.to_numeric(d["unidades_devueltas"], errors="coerce")
df_ = pd.to_datetime(d["fecha"], errors="coerce")
P(f"\n  Devoluciones: {len(d):,} registros, {d['unidades_devueltas'].sum():,.0f} unidades | fechas {df_.min().date()} a {df_.max().date()} | "
  f"unidades {d['unidades_devueltas'].describe().round(1).to_dict()} | por año {df_.dt.year.value_counts().sort_index().to_dict()}")
P(f"  Devoluciones por motivo (registros / unidades): {d.groupby('motivo')['unidades_devueltas'].agg(['count','sum']).to_dict('index')}")
P(f"  ¿Nº devoluciones ({len(d)}) == Nº filas de ventas negativas ({len(neg_v)})? {len(d)==len(neg_v)}")
dm = d.assign(fecha_mes=df_.dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m-%d"))
negk = neg_v[K].copy()
m = dm.merge(negk, on=K, how="left", indicator=True)
P(f"  Devoluciones cuya clave mes-tienda-SKU coincide con una fila de venta negativa: {int((m['_merge']=='both').sum())} de {len(dm)}")
m2 = dm.merge(neg_v[K + ["unidades_vendidas"]], on=K, how="inner")
P(f"     de esas, con unidades devueltas == -unidades_vendidas: {int((m2['unidades_devueltas'] == -m2['unidades_vendidas']).sum())}")
m3 = dm.merge(v[K], on=K, how="left", indicator=True)
P(f"  Devoluciones cuya clave existe en Ventas (cualquier valor): {int((m3['_merge']=='both').sum())} de {len(dm)}")

# historial precios
hp = raw["Historial_Precios_SKU"].copy()
for col in ["precio_lista", "costo_unitario"]: hp[col] = pd.to_numeric(hp[col], errors="coerce")
hd = pd.to_datetime(hp["fecha_vigencia_desde"], errors="coerce"); hh = pd.to_datetime(hp["fecha_vigencia_hasta"], errors="coerce")
hp["d"], hp["h"] = hd, hh
P(f"\n  Historial precios: {len(hp):,} filas, {hp['id_producto'].nunique()} SKUs | versiones por SKU {hp.groupby('id_producto').size().value_counts().sort_index().to_dict()} | "
  f"hasta<desde: {int((hh<hd).sum())} | precio<costo: {int((hp['precio_lista']<hp['costo_unitario']).sum())} | nulos costo: {int(hp['costo_unitario'].isna().sum())}")
hs = hp.sort_values(["id_producto", "d"]); nxt = hs.groupby("id_producto")["d"].shift(-1)
gap = (nxt - hs["h"]).dt.days
P(f"  Vigencias: SKUs con más de una vigencia abierta (hasta nulo): {int(hp[hh.isna()].groupby('id_producto').size().gt(1).sum())} | "
  f"solapamientos (siguiente desde <= hasta): {int((gap<=0).sum())} | huecos >1 día: {int((gap>1).sum())}")
last = hs.groupby("id_producto").tail(1).set_index("id_producto")
cmp_ = cfirst[["precio_lista", "costo_unitario"]].astype(float).join(last[["precio_lista", "costo_unitario"]], rsuffix="_hist", how="inner")
P(f"  Última vigencia vs catálogo: precio igual {int(np.isclose(cmp_['precio_lista'], cmp_['precio_lista_hist']).sum())}/{len(cmp_)} | "
  f"costo igual {int(np.isclose(cmp_['costo_unitario'], cmp_['costo_unitario_hist']).sum())}/{int(cmp_['costo_unitario'].notna().sum())} (con costo en catálogo)")
first = hs.groupby("id_producto").head(1).set_index("id_producto")
P(f"  Primera vigencia 'desde' == fecha_alta_catalogo: {int((first['fecha_vigencia_desde'] == cfirst.loc[first.index,'fecha_alta_catalogo']).sum())}/{len(first)}")
nocost = cfirst[cfirst["costo_unitario"].isna()].index
P(f"  De los SKUs sin costo en catálogo ({len(nocost)}), cuántos tienen costo en Historial: {int(hp[hp['id_producto'].isin(nocost)].groupby('id_producto')['costo_unitario'].apply(lambda x: x.notna().any()).sum())}")

# OC
oc = raw["Ordenes_Compra"].copy()
oc["unidades"] = pd.to_numeric(oc["unidades"], errors="coerce"); oc["costo_unitario_ars"] = pd.to_numeric(oc["costo_unitario_ars"], errors="coerce")
op = pd.to_datetime(oc["fecha_pedido"], errors="coerce"); orc = pd.to_datetime(oc["fecha_recepcion"], errors="coerce")
lt = (orc - op).dt.days
P(f"\n  OC: pedidos {op.min().date()} a {op.max().date()} | recepción {orc.min().date()} a {orc.max().date()} | "
  f"pedido > 2025-12-31: {int((op>'2025-12-31').sum())} | recepción > 2025-12-31: {int((orc>'2025-12-31').sum())} | recepción<pedido: {int((lt<0).sum())}")
P(f"  OC por año de pedido: {op.dt.year.value_counts().sort_index().to_dict()}")
P(f"  OC lead time real (días): {lt.describe(percentiles=[.05,.5,.95]).round(1).to_dict()}")
prov = raw["Proveedores"].copy()
for col in ["lead_time_dias", "pedido_minimo_unidades"]: prov[col] = pd.to_numeric(prov[col])
ltp = oc.assign(lt=lt).groupby("proveedor")["lt"].agg(["median", "mean", "min", "max"]).join(prov.set_index("proveedor")[["lead_time_dias", "pedido_minimo_unidades"]])
ltp["uds_bajo_minimo"] = oc.merge(prov, on="proveedor").assign(b=lambda x: x["unidades"] < x["pedido_minimo_unidades"]).groupby("proveedor")["b"].sum()
P("  Lead time real vs declarado por proveedor + OCs bajo pedido mínimo:\n" + ltp.round(1).to_string())
ocm = oc.merge(cfirst[["proveedor"]].rename(columns={"proveedor": "prov_cat"}), left_on="id_producto", right_index=True, how="left")
P(f"  OC con proveedor distinto al del catálogo (1ra ocurrencia): {int((ocm['proveedor'] != ocm['prov_cat']).sum())} de {len(oc)}")
oca = oc.assign(alta=pd.to_datetime(oc["id_producto"].map(cfirst["fecha_alta_catalogo"])), baja=pd.to_datetime(oc["id_producto"].map(cfirst["fecha_baja_catalogo"])))
P(f"  OC pedidas antes del alta del SKU: {int((op < oca['alta']).sum())} | después de la baja: {int((op > oca['baja']).sum())}")
occ = oc.assign(ccat=oc["id_producto"].map(cfirst["costo_unitario"].astype(float)))
occ["r"] = occ["costo_unitario_ars"] / occ["ccat"]
P(f"  Costo OC / costo catálogo: {occ['r'].describe(percentiles=[.05,.5,.95]).round(3).to_dict()}")

# presupuesto
pr = raw["Presupuesto_Ventas_Tienda_Categoria"].copy()
for col in ["presupuesto_venta_ars", "presupuesto_unidades"]: pr[col] = pd.to_numeric(pr[col], errors="coerce")
P(f"\n  Presupuesto: {pr['fecha_mes'].min()} a {pr['fecha_mes'].max()} | meses={pr['fecha_mes'].nunique()} tiendas={pr['id_tienda'].nunique()} cats={pr['categoria'].nunique()} | "
  f"filas en 0 venta: {int((pr['presupuesto_venta_ars']==0).sum()):,} ({(pr['presupuesto_venta_ars']==0).mean():.1%}) | negativos: {int((pr['presupuesto_venta_ars']<0).sum())} | "
  f"venta>0 con unidades=0: {int(((pr['presupuesto_venta_ars']>0)&(pr['presupuesto_unidades']==0)).sum())}")
P(f"  Presupuesto por año ($M): {(pr.assign(y=pr['fecha_mes'].str[:4]).groupby('y')['presupuesto_venta_ars'].sum()/1e6).round(1).to_dict()}")

# promociones
pm = raw["Promociones_Comerciales"].copy(); pm["descuento_pct"] = pd.to_numeric(pm["descuento_pct"], errors="coerce")
pi = pd.to_datetime(pm["fecha_inicio"], errors="coerce"); pf = pd.to_datetime(pm["fecha_fin"], errors="coerce")
P(f"\n  Promociones: {pi.min().date()} a {pf.max().date()} | fin<inicio: {int((pf<pi).sum())} | descuento fuera [0,100]: {pm.loc[(pm['descuento_pct']<0)|(pm['descuento_pct']>100),'descuento_pct'].tolist()} | "
  f"por año {pi.dt.year.value_counts().sort_index().to_dict()} | duración días {(pf-pi).dt.days.describe().round(1).to_dict()}")
cal = raw["Calendario"].copy(); cal["fecha"] = pd.to_datetime(cal["fecha"])
ev = cal.dropna(subset=["evento_especial"]).groupby([cal["fecha"].dt.year, "evento_especial"])["fecha"].agg(["min", "max"])
P("  Eventos en Calendario (min/max por año):\n" + ev.to_string())
chk = []
for _, r in pm.dropna(subset=["evento_asociado"]).iterrows():
    days = cal[(cal["fecha"] >= pd.to_datetime(r["fecha_inicio"])) & (cal["fecha"] <= pd.to_datetime(r["fecha_fin"]))]
    chk.append(r["evento_asociado"] in set(days["evento_especial"].dropna()))
P(f"  Promos con evento asociado cuyo rango coincide con ese evento en Calendario: {sum(chk)} de {len(chk)}")

# transferencias
tr = raw["Transferencias_Stock"].copy(); tr["unidades"] = pd.to_numeric(tr["unidades"], errors="coerce")
te = pd.to_datetime(tr["fecha_envio"], errors="coerce"); trc = pd.to_datetime(tr["fecha_recepcion"], errors="coerce")
P(f"\n  Transferencias: {te.min().date()} a {trc.max().date()} | recepción<envío: {int((trc<te).sum())} | origen==destino: {int((tr['origen']==tr['destino']).sum())} | "
  f"envío>2025-12-31: {int((te>'2025-12-31').sum())} | unidades {tr['unidades'].describe().round(1).to_dict()} | por año {te.dt.year.value_counts().sort_index().to_dict()}")
P(f"  Tipo: desde depósito {int((tr['origen']=='DEP-CENTRAL').sum())} | hacia depósito {int((tr['destino']=='DEP-CENTRAL').sum())} | tienda-tienda {int(((tr['origen']!='DEP-CENTRAL')&(tr['destino']!='DEP-CENTRAL')).sum())}")
P(f"  Días de tránsito: {(trc-te).dt.days.describe(percentiles=[.05,.5,.95]).round(1).to_dict()}")

# stock depósito
sd = raw["Stock_Deposito_Central"].copy(); sd["stock_disponible"] = pd.to_numeric(sd["stock_disponible"], errors="coerce")
P(f"\n  Stock depósito: {sd['fecha_mes'].min()} a {sd['fecha_mes'].max()} | SKUs {sd['id_producto'].nunique()} | negativos {int((sd['stock_disponible']<0).sum())} | "
  f"total unidades dic-2025: {sd.loc[sd['fecha_mes']=='2025-12-01','stock_disponible'].sum():,.0f}")

# costo almacenamiento
ca = raw["Costo_almacenamiento"].copy()
for col in ["precio_lista_promedio", "costo_mensual_almacenamiento_unidad_ars"]: ca[col] = pd.to_numeric(ca[col])
cn = c.assign(cat=c["categoria"].replace(CAT_MAP)).drop_duplicates("id_producto")
ca["precio_prom_catalogo"] = ca["categoria"].map(cn.groupby("cat")["precio_lista"].mean()).round(0)
ca["pct_real"] = (ca["costo_mensual_almacenamiento_unidad_ars"] / ca["precio_lista_promedio"] * 100).round(3)
P("  Costo_almacenamiento vs catálogo:\n" + ca.drop(columns="criterio").to_string() + f"\n  criterio: {ca['criterio'].unique().tolist()}")

# ----------------------------------------------------------------------------------------------
H("3. DATOS LIMPIOS (criterio V1 del TP1) — ANALITICA DESCRIPTIVA")
cat = c.copy(); cat["categoria"] = cat["categoria"].replace(CAT_MAP); cat = cat.drop_duplicates("id_producto")
ven = v.drop_duplicates(K).copy(); sto = s.drop_duplicates(K).copy()
ven.loc[ven["unidades_vendidas"] < 0, "unidades_vendidas"] = 0; ven.loc[ven["venta_neta"] < 0, "venta_neta"] = 0
sto.loc[sto["stock_disponible"] < 0, "stock_disponible"] = 0
for df in (ven, sto):
    df["fecha_mes"] = pd.to_datetime(df["fecha_mes"])
    df["categoria"] = df["id_producto"].map(cat.set_index("id_producto")["categoria"])
    df["region"] = df["id_tienda"].map(tiendas.set_index("id_tienda")["region"])
P(f"  Filas limpias ventas={len(ven):,} stock={len(sto):,}")
tot_v = ven["venta_neta"].sum(); tot_u = ven["unidades_vendidas"].sum()
P(f"  Venta total: ${tot_v/1e6:,.1f} M | unidades {tot_u:,.0f} | precio medio por unidad ${tot_v/tot_u:,.0f}")
P(f"  (crudo sin limpiar: venta ${v['venta_neta'].sum()/1e6:,.1f} M, unidades {v['unidades_vendidas'].sum():,.0f})")
y = ven.groupby(ven["fecha_mes"].dt.year).agg(venta=("venta_neta", "sum"), unidades=("unidades_vendidas", "sum"),
                                              skus=("id_producto", "nunique"), posiciones=("id_producto", "size"))
y["venta_M"] = y["venta"] / 1e6; y["var_%"] = y["venta"].pct_change() * 100
P("  Por año:\n" + y.round(1).to_string())
mens = ven.groupby("fecha_mes").agg(venta=("venta_neta", "sum"), unidades=("unidades_vendidas", "sum"))
stm = sto.groupby("fecha_mes").agg(stock=("stock_disponible", "sum"), transito=("stock_en_transito", "sum"))
mens = mens.join(stm); mens["cobertura_meses"] = mens["stock"] / mens["unidades"]
mens.to_csv(os.path.join(RES, "serie_mensual.csv"), encoding="utf-8-sig")
P(f"  Primer mes con ventas: {mens.index.min().date()} | ventas por mes 2022 ($M): {(mens.loc['2022','venta']/1e6).round(1).tolist()}")
P(f"  Nº tiendas con filas por año: {ven.groupby(ven['fecha_mes'].dt.year)['id_tienda'].nunique().to_dict()} | SKUs activos por año: {ven[ven['unidades_vendidas']>0].groupby(ven['fecha_mes'].dt.year)['id_producto'].nunique().to_dict()}")
P(f"  Posiciones (filas) por mes: primero {ven.groupby('fecha_mes').size().iloc[0]} último {ven.groupby('fecha_mes').size().iloc[-1]}")
# estacionalidad
for rng, lab in [(("2022-01-01", "2025-12-31"), "2022-2025"), (("2023-01-01", "2025-12-31"), "2023-2025"), (("2025-01-01", "2025-12-31"), "2025")]:
    sub = mens.loc[rng[0]:rng[1]].copy()
    sub["idx"] = sub.groupby(sub.index.year)["venta"].transform(lambda x: x / x.mean() * 100)
    P(f"  Índice estacional venta (100=prom. anual, promedio por mes) {lab}: {sub.groupby(sub.index.month)['idx'].mean().round(0).to_dict()}")
    sub["idxu"] = sub.groupby(sub.index.year)["unidades"].transform(lambda x: x / x.mean() * 100)
    P(f"  Índice estacional UNIDADES {lab}: {sub.groupby(sub.index.month)['idxu'].mean().round(0).to_dict()}")
# categoría, región, tienda
bycat = ven.groupby("categoria").agg(venta=("venta_neta", "sum"), unidades=("unidades_vendidas", "sum"))
bycat["%venta"] = bycat["venta"] / tot_v * 100
bycat["skus"] = cat.groupby("categoria").size(); bycat["%skus"] = bycat["skus"] / len(cat) * 100
bycat["margen_lista_%"] = cat.groupby("categoria").apply(lambda x: ((x["precio_lista"] - x["costo_unitario"]) / x["precio_lista"]).mean() * 100)
P("  Por categoría:\n" + bycat.sort_values("venta", ascending=False).round(1).to_string())
P(f"  Margen teórico de lista promedio catálogo: {((cat['precio_lista']-cat['costo_unitario'])/cat['precio_lista']).mean()*100:.1f}%")
byreg = ven.groupby("region")["venta_neta"].sum().sort_values(ascending=False)
P(f"  Por región %: {(byreg/tot_v*100).round(1).to_dict()} | tiendas por región: {tiendas['region'].value_counts().to_dict()}")
byt = ven.groupby("id_tienda").agg(venta=("venta_neta", "sum")).join(tiendas.set_index("id_tienda")[["nombre_tienda", "region", "formato", "m2_venta", "fecha_apertura"]])
byt["m2_venta"] = byt["m2_venta"].astype(float); byt["venta_M"] = byt["venta"] / 1e6
byt["venta_por_m2"] = byt["venta"] / byt["m2_venta"]
byt["%"] = byt["venta"] / tot_v * 100
byt = byt.sort_values("venta", ascending=False); byt["%acum"] = byt["%"].cumsum()
P("  Por tienda:\n" + byt.drop(columns="venta").round(1).to_string())
P(f"  Correlación venta tienda vs m2: {byt['venta'].corr(byt['m2_venta']):.3f}")
P(f"  Por formato: {(ven.merge(tiendas[['id_tienda','formato']], on='id_tienda').groupby('formato')['venta_neta'].sum()/tot_v*100).round(1).to_dict()}")
# Pareto SKU
bysku = ven.groupby("id_producto")["venta_neta"].sum().sort_values(ascending=False)
bysku = bysku[bysku > 0]; cum = bysku.cumsum() / bysku.sum()
n80 = int((cum < 0.8).sum() + 1)
P(f"  Pareto: {n80} de {len(bysku)} SKUs con venta ({n80/len(bysku):.1%}) explican el 80% de la venta | top 10% SKUs = {cum.iloc[int(len(bysku)*0.1)-1]:.1%} de la venta")
bysku25 = ven[ven["fecha_mes"].dt.year == 2025].groupby("id_producto")["venta_neta"].sum().sort_values(ascending=False)
bysku25 = bysku25[bysku25 > 0]; c25 = bysku25.cumsum() / bysku25.sum()
P(f"  Pareto 2025: {int((c25<0.8).sum()+1)} de {len(bysku25)} SKUs explican el 80%")
# stats por posición
pos = ven[ven["fecha_mes"] >= "2025-01-01"]
P(f"  Estadísticas por fila SKU-tienda-mes 2025 (unidades): {pos['unidades_vendidas'].describe(percentiles=[.25,.5,.75,.95,.99]).round(2).to_dict()}")
P(f"  Estadísticas por fila SKU-tienda-mes 2025 (venta_neta): {pos['venta_neta'].describe(percentiles=[.25,.5,.75,.95,.99]).round(0).to_dict()}")
sd25 = sto[sto["fecha_mes"] == "2025-12-01"]
P(f"  Stock dic-2025 por posición: {sd25['stock_disponible'].describe(percentiles=[.25,.5,.75,.95,.99]).round(1).to_dict()} | posiciones con stock>0: {int((sd25['stock_disponible']>0).sum()):,} | "
  f"SKUs con stock>0: {sd25.loc[sd25['stock_disponible']>0,'id_producto'].nunique()} | de ellos Activos: {sd25.loc[sd25['stock_disponible']>0,'id_producto'].map(cat.set_index('id_producto')['estado']).eq('Activo').pipe(lambda x: sd25.loc[sd25['stock_disponible']>0].assign(a=x).query('a')['id_producto'].nunique())}")
for mth in ["2023-01-01"]:
    P(f"  Posiciones con stock>0 en {mth}: {int((sto[sto['fecha_mes']==mth]['stock_disponible']>0).sum()):,}")
P(f"  Catálogo: {len(cat)} SKUs | estado {cat['estado'].value_counts().to_dict()} | activos con alta <= dic-2025 y sin baja: {int(((cat['estado']=='Activo')).sum())}")
# relaciones
yr = ven.assign(y=ven["fecha_mes"].dt.year).groupby("y")["unidades_vendidas"].sum()
ys = sto.assign(y=sto["fecha_mes"].dt.year).groupby("y")["stock_disponible"].mean()
P(f"  Unidades vendidas por año: {yr.to_dict()} | stock promedio mensual por año: {ys.round(0).to_dict()}")
P(f"  Ratio 2025/2023 ventas($)={y.loc[2025,'venta']/y.loc[2023,'venta']:.2f} unidades={yr[2025]/yr[2023]:.2f} stock prom={ys[2025]/ys[2023]:.2f}")
P(f"  Cobertura agregada (stock/unidades mes): ene-23={mens.loc['2023-01-01','cobertura_meses']:.2f} dic-25={mens.loc['2025-12-01','cobertura_meses']:.2f} prom 2023={mens.loc['2023','cobertura_meses'].mean():.2f} prom 2025={mens.loc['2025','cobertura_meses'].mean():.2f}")
j = ven.merge(sto[K + ["stock_disponible", "stock_en_transito"]].assign(fecha_mes=lambda x: pd.to_datetime(x["fecha_mes"])), on=K)
P(f"  Correlación fila a fila unidades vs stock: {j['unidades_vendidas'].corr(j['stock_disponible']):.3f}")
P(f"  Filas con venta>0 y stock=0 en el mismo mes: {int(((j['unidades_vendidas']>0)&(j['stock_disponible']==0)).sum()):,} | venta > stock: {int((j['unidades_vendidas']>j['stock_disponible']).sum()):,}")
P(f"  Filas con 0 ventas y 0 stock: {int(((j['unidades_vendidas']==0)&(j['stock_disponible']==0)).sum()):,} | 0 ventas con stock>0: {int(((j['unidades_vendidas']==0)&(j['stock_disponible']>0)).sum()):,}")
# presupuesto vs real
rc = ven.groupby([ven["fecha_mes"].dt.strftime("%Y-%m-%d"), "id_tienda", "categoria"])["venta_neta"].sum().rename("real")
pv = pr.set_index(["fecha_mes", "id_tienda", "categoria"])["presupuesto_venta_ars"].to_frame().join(rc, how="outer")
P(f"  Presupuesto vs real: celdas solo en presupuesto={int(pv['real'].isna().sum())} solo en real={int(pv['presupuesto_venta_ars'].isna().sum())}")
pvy = pv.groupby(pv.index.get_level_values(0).str[:4]).sum()
pvy["cumpl_%"] = pvy["real"] / pvy["presupuesto_venta_ars"] * 100
P("  Presupuesto vs real por año ($M):\n" + (pvy[["presupuesto_venta_ars", "real"]] / 1e6).round(1).join(pvy["cumpl_%"].round(1)).to_string())
pz = pv[(pv["presupuesto_venta_ars"] == 0) & (pv["real"] > 0)]
P(f"  Celdas con presupuesto 0 y venta real >0: {len(pz):,} | presupuesto >0 y real 0/nulo: {int(((pv['presupuesto_venta_ars']>0)&(pv['real'].fillna(0)==0)).sum()):,}")
pvc = pv.groupby(level=2).sum(); pvc["cumpl_%"] = pvc["real"] / pvc["presupuesto_venta_ars"] * 100
P("  Cumplimiento por categoría (total período): " + str(pvc["cumpl_%"].round(1).to_dict()))
pvm = pv.groupby(level=0).sum(); pvm["cumpl_%"] = pvm["real"] / pvm["presupuesto_venta_ars"] * 100
pvm.to_csv(os.path.join(RES, "presupuesto_vs_real_mensual.csv"), encoding="utf-8-sig")
P(f"  Cumplimiento mensual (min/mediana/max, meses con presupuesto>0): {pvm.loc[pvm['presupuesto_venta_ars']>0,'cumpl_%'].describe().round(1).to_dict()}")
# devoluciones vs ventas
dv = d.assign(y=df_.dt.year).groupby("y")["unidades_devueltas"].sum()
P(f"  Tasa devolución (unidades devueltas / vendidas) por año: {(dv / yr * 100).round(2).to_dict()}")
P(f"  Unidades en ventas negativas (crudo) por año: {neg_v.assign(y=neg_v['fecha_mes'].str[:4]).groupby('y')['unidades_vendidas'].sum().to_dict()}")

byt.to_csv(os.path.join(RES, "venta_por_tienda.csv"), encoding="utf-8-sig")
bycat.to_csv(os.path.join(RES, "venta_por_categoria.csv"), encoding="utf-8-sig")
ltp.to_csv(os.path.join(RES, "leadtime_proveedores.csv"), encoding="utf-8-sig")

# ----------------------------------------------------------------------------------------------
H("4. GRAFICOS")
def save(fig, n): fig.tight_layout(); fig.savefig(os.path.join(GRA, n), dpi=130); plt.close(fig); P("  ->", n)
fig, ax = plt.subplots(figsize=(11, 4)); ax.plot(mens.index, mens["venta"] / 1e6, marker="o", ms=3)
ax.set_title("Venta neta mensual ($ M) — ene-2022 a dic-2025"); ax.grid(alpha=.3); save(fig, "01_venta_mensual.png")
fig, ax = plt.subplots(figsize=(11, 4)); ax.plot(mens.index, mens["unidades"], label="Unidades vendidas"); ax2 = ax.twinx()
ax2.plot(mens.index, mens["stock"], color="tab:orange", label="Stock disponible"); ax.set_title("Unidades vendidas vs stock disponible (tiendas)")
ax.legend(loc="upper left"); ax2.legend(loc="upper right"); ax.grid(alpha=.3); save(fig, "02_unidades_vs_stock.png")
fig, ax = plt.subplots(figsize=(11, 4)); ax.plot(mens.index, mens["cobertura_meses"]); ax.set_title("Cobertura agregada (stock / unidades del mes)"); ax.grid(alpha=.3); save(fig, "03_cobertura.png")
sub = mens.loc["2023":"2025"].copy(); sub["idx"] = sub.groupby(sub.index.year)["venta"].transform(lambda x: x / x.mean() * 100)
fig, ax = plt.subplots(figsize=(8, 4)); sub.groupby(sub.index.month)["idx"].mean().plot.bar(ax=ax); ax.axhline(100, color="k", lw=.8)
ax.set_title("Índice estacional de venta 2023-2025 (100 = promedio anual)"); save(fig, "04_estacionalidad.png")
fig, ax = plt.subplots(figsize=(8, 4)); bycat.sort_values("venta")[["%venta", "%skus"]].plot.barh(ax=ax); ax.set_title("Categoría: % venta vs % SKUs"); save(fig, "05_categoria_venta_vs_skus.png")
fig, ax = plt.subplots(figsize=(7, 4)); (byreg / tot_v * 100).plot.bar(ax=ax); ax.set_title("% de venta por región"); save(fig, "06_region.png")
fig, ax = plt.subplots(figsize=(8, 4)); ax.plot(np.arange(1, len(cum) + 1) / len(cum) * 100, cum.values * 100); ax.axhline(80, ls="--", c="gray"); ax.axvline(n80 / len(bysku) * 100, ls="--", c="gray")
ax.set_xlabel("% de SKUs"); ax.set_ylabel("% venta acumulada"); ax.set_title("Pareto de venta por SKU (2022-2025)"); ax.grid(alpha=.3); save(fig, "07_pareto_sku.png")
fig, ax = plt.subplots(figsize=(11, 5)); byt.sort_values("venta")["venta_M"].plot.barh(ax=ax); ax.set_title("Venta por tienda ($ M, 2022-2025)"); save(fig, "08_tiendas.png")
fig, ax = plt.subplots(figsize=(11, 4)); pvmi = pvm.copy(); pvmi.index = pd.to_datetime(pvmi.index)
ax.plot(pvmi.index, pvmi["real"] / 1e6, label="Real"); ax.plot(pvmi.index, pvmi["presupuesto_venta_ars"] / 1e6, label="Presupuesto"); ax.legend(); ax.grid(alpha=.3)
ax.set_title("Venta real vs presupuesto ($ M)"); save(fig, "09_presupuesto_vs_real.png")
fig, ax = plt.subplots(figsize=(8, 4)); d.groupby("motivo")["unidades_devueltas"].sum().sort_values().plot.barh(ax=ax); ax.set_title("Unidades devueltas por motivo"); save(fig, "10_devoluciones_motivo.png")
fig, ax = plt.subplots(figsize=(8, 4)); ax.scatter(ltp["lead_time_dias"], ltp["median"]); [ax.annotate(i[-1], (r["lead_time_dias"], r["median"])) for i, r in ltp.iterrows()]
mx = max(ltp["lead_time_dias"].max(), ltp["median"].max()); ax.plot([0, mx], [0, mx], ls="--", c="gray"); ax.set_xlabel("Lead time declarado"); ax.set_ylabel("Lead time real (mediana OC)")
ax.set_title("Lead time declarado vs real por proveedor"); save(fig, "11_leadtime.png")
fig, axs = plt.subplots(1, 2, figsize=(11, 4)); pos25 = pos[pos["unidades_vendidas"] > 0]
axs[0].hist(pos25["unidades_vendidas"].clip(upper=pos25["unidades_vendidas"].quantile(.99)), bins=40); axs[0].set_title("Unidades por fila SKU-tienda-mes 2025 (>0, p99)")
st = sd25[sd25["stock_disponible"] > 0]["stock_disponible"]; axs[1].hist(st.clip(upper=st.quantile(.99)), bins=40); axs[1].set_title("Stock por posición dic-2025 (>0, p99)"); save(fig, "12_distribuciones.png")
LOG.close()
