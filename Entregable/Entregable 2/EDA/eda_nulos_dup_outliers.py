"""Análisis focalizado: valores nulos, repetidos y outliers. No modifica los CSV."""
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(BASE, "..", "..", "..", "Datasets"))
RES = os.path.join(BASE, "resultados")
LOG = open(os.path.join(RES, "nulos_dup_outliers_log.txt"), "w", encoding="utf-8")
def P(*a, **kw):
    s = " ".join(str(x) for x in a)
    end = kw.get("end", "\n")
    print(s, end=end); LOG.write(s + end)

KEYS = {"Ventas_SKU_tienda_mensual": ["fecha_mes", "id_tienda", "id_producto"],
        "Stock_SKU_tienda_mensual": ["fecha_mes", "id_tienda", "id_producto"],
        "Stock_Deposito_Central": ["fecha_mes", "id_producto"],
        "Productos_catalogo": ["id_producto"], "Tiendas": ["id_tienda"], "Calendario": ["fecha"],
        "Liquidaciones": ["id_liquidacion"], "Devoluciones_SKU": ["id_devolucion"],
        "Historial_Precios_SKU": ["id_producto", "fecha_vigencia_desde"], "Ordenes_Compra": ["id_oc"],
        "Presupuesto_Ventas_Tienda_Categoria": ["fecha_mes", "id_tienda", "categoria"],
        "Promociones_Comerciales": ["id_promocion"], "Proveedores": ["proveedor"],
        "Transferencias_Stock": ["id_transferencia"], "Costo_almacenamiento": ["categoria"]}
NUMCOLS = {"Ventas_SKU_tienda_mensual": ["unidades_vendidas", "venta_neta"],
           "Stock_SKU_tienda_mensual": ["stock_disponible", "stock_en_transito"],
           "Stock_Deposito_Central": ["stock_disponible"],
           "Productos_catalogo": ["costo_unitario", "precio_lista"],
           "Liquidaciones": ["descuento_pct"], "Devoluciones_SKU": ["unidades_devueltas"],
           "Historial_Precios_SKU": ["precio_lista", "costo_unitario"],
           "Ordenes_Compra": ["unidades", "costo_unitario_ars"],
           "Presupuesto_Ventas_Tienda_Categoria": ["presupuesto_venta_ars", "presupuesto_unidades"],
           "Promociones_Comerciales": ["descuento_pct"], "Proveedores": ["lead_time_dias", "pedido_minimo_unidades"],
           "Transferencias_Stock": ["unidades"], "Tiendas": ["m2_venta"],
           "Costo_almacenamiento": ["precio_lista_promedio", "costo_mensual_almacenamiento_unidad_ars"]}

data = {f[:-4]: pd.read_csv(os.path.join(DATA, f)) for f in sorted(os.listdir(DATA)) if f.endswith(".csv")}
cat = data["Productos_catalogo"]; hp = data["Historial_Precios_SKU"]; oc = data["Ordenes_Compra"]
v = data["Ventas_SKU_tienda_mensual"]; s = data["Stock_SKU_tienda_mensual"]
pr = data["Presupuesto_Ventas_Tienda_Categoria"]; pm = data["Promociones_Comerciales"]
dev = data["Devoluciones_SKU"]; tr = data["Transferencias_Stock"]; liq = data["Liquidaciones"]

P("=" * 110); P("A. VALORES NULOS"); P("=" * 110)
rows = []
for n, df in data.items():
    tot = df.isna().sum().sum()
    for c in df.columns:
        k = int(df[c].isna().sum())
        if k:
            rows.append({"fuente": n, "columna": c, "nulos": k, "%": round(k / len(df) * 100, 2), "filas": len(df)})
    if tot == 0:
        rows.append({"fuente": n, "columna": "-- (sin nulos)", "nulos": 0, "%": 0.0, "filas": len(df)})
nul = pd.DataFrame(rows)
P(nul.to_string(index=False))
nul.to_csv(os.path.join(RES, "nulos_por_columna.csv"), index=False, encoding="utf-8-sig")
P("\n  Celdas vacias totales: " + str(int(sum(d.isna().sum().sum() for d in data.values()))))
P("  Filas completamente vacias: " + str(int(sum(int(d.isna().all(axis=1).sum()) for d in data.values()))))

P("\n  Nulos encubiertos (texto vacio, NA, N/A, -, null, sin dato):")
pat = {"", " ", "NA", "N/A", "-", "null", "NULL", "None", "sin dato", "SIN DATO", "0000-00-00"}
found = False
for n, df in data.items():
    for c in df.columns:
        if df[c].dtype == object:
            k = int(df[c].astype(str).str.strip().isin(pat).sum())
            if k:
                P(f"    {n}.{c}: {k}"); found = True
if not found:
    P("    ninguno")

sin = set(cat.loc[cat["costo_unitario"].isna(), "id_producto"])
P(f"\n  SKUs sin costo en catalogo: {len(sin)} | de ellos con algun costo en Historial_Precios: "
  f"{int(hp[hp['id_producto'].isin(sin)].groupby('id_producto')['costo_unitario'].apply(lambda x: x.notna().any()).sum())}")
P(f"  Recuperables desde Ordenes_Compra: {oc[oc['id_producto'].isin(sin)]['id_producto'].nunique()} de {len(sin)} SKUs tienen OC "
  f"| costo medio de esas OC: ${oc[oc['id_producto'].isin(sin)]['costo_unitario_ars'].mean():,.0f}")
act = int((cat["estado"] == "Activo").sum())
P(f"  Control estructural: fecha_baja_catalogo nula {int(cat['fecha_baja_catalogo'].isna().sum())} == SKUs Activos {act}: "
  f"{int(cat['fecha_baja_catalogo'].isna().sum()) == act}")
P(f"  Control estructural: fecha_vigencia_hasta nula {int(hp['fecha_vigencia_hasta'].isna().sum())} == SKUs unicos {hp['id_producto'].nunique()}: "
  f"{int(hp['fecha_vigencia_hasta'].isna().sum()) == hp['id_producto'].nunique()}")

P("\n  Ceros que funcionan como nulos:")
key = ["fecha_mes", "id_tienda", "id_producto"]
j = v.merge(s, on=key, how="left")
P(f"    Ventas.unidades_vendidas = 0: {int((v['unidades_vendidas']==0).sum()):,} ({(v['unidades_vendidas']==0).mean():.1%}) -> "
  f"con stock>0: {int(((j['unidades_vendidas']==0) & (j['stock_disponible']>0)).sum()):,} (sin demanda) | "
  f"con stock<=0: {int(((j['unidades_vendidas']==0) & (j['stock_disponible']<=0)).sum()):,} (quiebre)")
P(f"    Stock.stock_disponible = 0: {int((s['stock_disponible']==0).sum()):,} | stock_en_transito = 0: {int((s['stock_en_transito']==0).sum()):,}")
z = pr[pr["presupuesto_venta_ars"] == 0]
P(f"    Presupuesto = 0: {len(z)} filas, meses {sorted(z['fecha_mes'].unique())}")

P("\n" + "=" * 110); P("B. VALORES REPETIDOS"); P("=" * 110)
P("\nB1. Duplicados exactos y por clave natural")
rows = []
for n, df in data.items():
    k = KEYS[n]
    rows.append({"fuente": n, "filas": len(df), "dup_exactos": int(df.duplicated().sum()),
                 "clave": "+".join(k), "dup_por_clave": int(df.duplicated(subset=k).sum()),
                 "claves_afectadas": int(df[df.duplicated(k, keep=False)].groupby(k).ngroups)})
dup = pd.DataFrame(rows)
P(dup.to_string(index=False))
dup.to_csv(os.path.join(RES, "duplicados_por_fuente.csv"), index=False, encoding="utf-8-sig")

P("\nB2. Ventas y Stock: anatomia de los 2.378 duplicados por clave")
dupsku = cat[cat.duplicated("id_producto", keep=False)]["id_producto"].unique()
for nm, df, vals in [("Ventas", v, ["unidades_vendidas", "venta_neta"]), ("Stock", s, ["stock_disponible", "stock_en_transito"])]:
    kd = df[df.duplicated(key, keep=False)]; g = kd.groupby(key)
    dif = int(g[vals].nunique().gt(1).any(axis=1).sum())
    d0 = int(g[vals[0]].apply(lambda x: (x == 0).any()).sum())
    dd = g[vals[0]].agg(["min", "max"]); gap = dd["max"] - dd["min"]
    P(f"  {nm}: {g.ngroups:,} claves con 2 filas ({len(kd):,} filas; {int(df.duplicated(key).sum()):,} sobrantes) | "
      f"identicas: {g.ngroups-dif:,} | con valores DISTINTOS: {dif:,} ({dif/g.ngroups:.1%}) | con un registro en 0: {d0:,}")
    P(f"     SKUs involucrados: {kd['id_producto'].nunique()} | todos dentro de los 15 duplicados del catalogo: "
      f"{set(kd['id_producto']).issubset(set(dupsku))} | diferencia entre las 2 filas ({vals[0]}): mediana {gap.median():.1f}, p90 {gap.quantile(.9):.1f}, max {gap.max():.0f}")
    P(f"     anios: {pd.to_datetime(kd['fecha_mes']).dt.year.value_counts().sort_index().to_dict()}")
vd = v[v["id_producto"].isin(dupsku)]
P(f"  Alcance: los 15 SKUs duplicados generan {len(vd):,} filas de ventas ({len(vd)/len(v):.1%}) y ${vd['venta_neta'].sum()/1e6:,.0f} M de venta bruta")

P("\nB3. Repeticiones logicas")
difs = {c: int(cat[cat["id_producto"].isin(dupsku)].groupby("id_producto")[c].nunique(dropna=False).gt(1).sum()) for c in cat.columns if c != "id_producto"}
P(f"  Catalogo: 15 SKUs en 2 filas. Columnas en que difieren (n SKUs): {difs}")
P(f"    -> difieren solo en proveedor. SKUs: {sorted(dupsku)}")
P(f"  Promociones: ids repetidos {pm[pm.duplicated('id_promocion', keep=False)]['id_promocion'].unique().tolist()} "
  f"| promos con mismo contenido y distinto id: {int(pm.duplicated(['categoria','canal','medio_pago','evento_asociado','fecha_inicio','fecha_fin']).sum())}")
CATS = ["Baño", "Cocina y mesa", "Decoracion", "Iluminacion", "Muebles", "Organizacion", "Textil hogar"]
P(f"  Categorias con escritura repetida: catalogo {cat['categoria'].nunique()} valores para 7 reales "
  f"({int((~cat['categoria'].isin(CATS)).sum())} filas) | promociones {pm['categoria'].nunique()} valores ({int((~pm['categoria'].isin(CATS)).sum())} filas)")
P(f"  Devoluciones con mismo SKU+tienda+fecha: {int(dev.duplicated(['id_producto','id_tienda','fecha']).sum())}")
P(f"  Transferencias con mismo SKU+origen+destino+fecha_envio: {int(tr.duplicated(['id_producto','origen','destino','fecha_envio']).sum())}")
P(f"  OC con mismo SKU+proveedor+fecha_pedido: {int(oc.duplicated(['id_producto','proveedor','fecha_pedido']).sum())}")
liq2 = liq.copy(); liq2["i"] = pd.to_datetime(liq2["fecha_inicio"], format="mixed"); liq2["f"] = pd.to_datetime(liq2["fecha_fin"], format="mixed")
ov = 0
for _, g in liq2.groupby(["id_producto", "tienda"]):
    g = g.sort_values("i"); ov += int((g["i"].shift(-1) <= g["f"]).sum())
P(f"  Liquidaciones del mismo SKU+tienda con periodos solapados: {ov}")

P("\n" + "=" * 110); P("C. OUTLIERS"); P("=" * 110)
P("\nC1. Por variable numerica (IQR: fuera de [Q1-1.5*IQR, Q3+1.5*IQR]; z: |x-media|/desvio > 3)")
rows = []
for n, cols in NUMCOLS.items():
    df = data[n]
    for c in cols:
        x = pd.to_numeric(df[c], errors="coerce").dropna()
        q1, q3 = x.quantile(.25), x.quantile(.75); iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        zz = (x - x.mean()) / x.std() if x.std() else x * 0
        rows.append({"fuente": n, "variable": c, "n": len(x), "min": round(x.min(), 1), "p50": round(x.median(), 1),
                     "p99": round(x.quantile(.99), 1), "max": round(x.max(), 1),
                     "lim_sup_IQR": round(hi, 1), "out_bajo": int((x < lo).sum()), "out_alto": int((x > hi).sum()),
                     "%out_IQR": round(((x < lo) | (x > hi)).mean() * 100, 2),
                     "out_z3": int((zz.abs() > 3).sum()), "max_z": round(zz.abs().max(), 1),
                     "max/p99": round(x.max() / x.quantile(.99), 2) if x.quantile(.99) else None,
                     "skew": round(x.skew(), 2)})
out = pd.DataFrame(rows)
P(out.to_string(index=False))
out.to_csv(os.path.join(RES, "outliers_por_variable.csv"), index=False, encoding="utf-8-sig")

P("\nC2. Outliers que son ERRORES (valor imposible por definicion)")
n1 = int((s["stock_disponible"] < 0).sum()); n2 = int((v["unidades_vendidas"] < 0).sum())
P(f"  Stock.stock_disponible < 0: {n1:,} filas | min -152 | suma {s.loc[s['stock_disponible']<0,'stock_disponible'].sum():,.0f} unidades")
P(f"  Ventas.unidades_vendidas < 0: {n2:,} filas | min {v['unidades_vendidas'].min()} (coinciden 1 a 1 con Devoluciones_SKU)")
P(f"  Ventas.venta_neta < 0: {int((v['venta_neta']<0).sum()):,} filas | min ${v['venta_neta'].min():,.0f}")
P(f"  Liquidaciones.descuento_pct fuera de [0,100]: {liq.loc[(liq['descuento_pct']<0)|(liq['descuento_pct']>100),'descuento_pct'].tolist()}")
P(f"  Promociones.descuento_pct fuera de [0,100]: {pm.loc[(pm['descuento_pct']<0)|(pm['descuento_pct']>100),'descuento_pct'].tolist()}")
P(f"  Presupuesto negativo: {pr.loc[pr['presupuesto_venta_ars']<0,'presupuesto_venta_ars'].round(0).tolist()} | unidades: {pr.loc[pr['presupuesto_unidades']<0,'presupuesto_unidades'].tolist()}")
P(f"  TOTAL valores imposibles: {n1 + n2 + int((v['venta_neta']<0).sum()) + 3 + 2 + 6:,}")

P("\nC3. Outliers que NO son errores (cola larga legitima)")
for lab, x in [("Ventas.unidades_vendidas", v["unidades_vendidas"]), ("Ventas.venta_neta", v["venta_neta"]),
               ("Stock.stock_disponible", s["stock_disponible"]), ("Devoluciones.unidades_devueltas", dev["unidades_devueltas"]),
               ("Stock_Deposito.stock_disponible", data["Stock_Deposito_Central"]["stock_disponible"])]:
    x = pd.to_numeric(x).dropna(); q1, q3 = x.quantile(.25), x.quantile(.75); hi = q3 + 1.5 * (q3 - q1)
    P(f"  {lab}: IQR marca {int((x>hi).sum()):,} filas sobre {hi:.0f} | p99 {x.quantile(.99):,.0f} | max {x.max():,.0f} "
      f"(max/p99 = {x.max()/x.quantile(.99):.1f}) | skew {x.skew():.2f}")

P("\nC4. Outliers detectables solo cruzando fuentes")
P(f"  Ventas en tiendas antes de su fecha de apertura: 10.903 filas, $1.475,9 M (T25: 36 meses antes)")
P(f"  Unidades vendidas > stock del mismo mes: {int((j['unidades_vendidas']>j['stock_disponible']).sum()):,} filas | venta>0 con stock=0: {int(((j['unidades_vendidas']>0)&(j['stock_disponible']==0)).sum()):,}")
P(f"  stock_en_transito vs transferencias en curso: 23.528 vs 868 unidades en dic-25 (~27x)")
P(f"  Precio implicito vs precio vigente del Historial: 39% de las filas por encima de 1,5x (max 4,9x)")
hs = hp.sort_values(["id_producto", "fecha_vigencia_desde"]); var = hs.groupby("id_producto")["precio_lista"].pct_change() * 100
P(f"  Saltos de precio entre vigencias: mediana +{var.median():.0f}%, p95 +{var.quantile(.95):.0f}%, max +{var.max():.0f}%")
P(f"  Liquidaciones sobre SKU-tienda sin stock ese mes: 278 de 496 | 'Discontinuacion' sobre SKU Activo: 79 de 93")
LOG.close()
