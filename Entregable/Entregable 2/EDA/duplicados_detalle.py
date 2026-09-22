"""Forense de los duplicados por clave en Ventas y Stock SKU-tienda-mes."""
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(BASE, "..", "..", "..", "Datasets"))
RES = os.path.join(BASE, "resultados")
LOG = open(os.path.join(RES, "duplicados_detalle_log.txt"), "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.max_rows", 80)
rd = lambda n: pd.read_csv(os.path.join(DATA, n + ".csv"))

K = ["fecha_mes", "id_tienda", "id_producto"]
v = rd("Ventas_SKU_tienda_mensual").reset_index().rename(columns={"index": "fila"})
s = rd("Stock_SKU_tienda_mensual").reset_index().rename(columns={"index": "fila"})
cat = rd("Productos_catalogo"); tiendas = rd("Tiendas")
dupsku = cat[cat.duplicated("id_producto", keep=False)]["id_producto"].unique().tolist()

P("=" * 105); P("1. ALCANCE: ¿QUE FILAS ESTAN DUPLICADAS?"); P("=" * 105)
for nm, df in [("Ventas", v), ("Stock", s)]:
    d = df[df.duplicated(K, keep=False)]
    P(f"  {nm}: {len(df):,} filas; {len(d):,} en claves repetidas ({len(d)/len(df):.2%}); "
      f"{df.duplicated(K).sum():,} sobrantes; filas por clave: {d.groupby(K).size().value_counts().to_dict()}")
kv = set(map(tuple, v[v.duplicated(K, keep=False)][K].drop_duplicates().values))
ks = set(map(tuple, s[s.duplicated(K, keep=False)][K].drop_duplicates().values))
P(f"  ¿Las claves duplicadas de Ventas y Stock son las MISMAS? {kv == ks} (ventas {len(kv):,}, stock {len(ks):,}, comunes {len(kv & ks):,})")

P("\n  ¿Se duplica TODA la historia de esos 15 SKUs o solo parte?")
rows = []
for sku in sorted(dupsku):
    tot = int((v["id_producto"] == sku).sum())
    dd = v[(v["id_producto"] == sku) & v.duplicated(K, keep=False)]
    meses = pd.to_datetime(v.loc[v["id_producto"] == sku, "fecha_mes"])
    rows.append({"sku": sku, "categoria": cat.loc[cat["id_producto"] == sku, "categoria"].iloc[0],
                 "proveedores": " / ".join(cat.loc[cat["id_producto"] == sku, "proveedor"].tolist()),
                 "alta": cat.loc[cat["id_producto"] == sku, "fecha_alta_catalogo"].iloc[0],
                 "filas_ventas": tot, "filas_duplicadas": len(dd), "%": round(len(dd) / tot * 100, 1),
                 "primer_mes": meses.min().strftime("%Y-%m"), "ultimo_mes": meses.max().strftime("%Y-%m"),
                 "tiendas": v.loc[v["id_producto"] == sku, "id_tienda"].nunique()})
t = pd.DataFrame(rows)
P(t.to_string(index=False))
P(f"\n  -> En los 15 SKUs, el {t['filas_duplicadas'].sum()/t['filas_ventas'].sum():.1%} de sus filas está duplicado. "
  f"SKUs con el 100% duplicado: {int((t['%']==100).sum())} de 15")
P(f"  -> Fuera de esos 15 SKUs no hay ni una clave repetida: {int(v[v.duplicated(K, keep=False) & ~v['id_producto'].isin(dupsku)].shape[0])} filas")
t.to_csv(os.path.join(RES, "duplicados_por_sku.csv"), index=False, encoding="utf-8-sig")

P("\n" + "=" * 105); P("2. ¿COMO SE UBICAN EN EL ARCHIVO? (pistas sobre el origen)"); P("=" * 105)
for nm, df in [("Ventas", v), ("Stock", s)]:
    d = df[df.duplicated(K, keep=False)].sort_values(K + ["fila"])
    g = d.groupby(K)["fila"].agg(["min", "max"])
    dist = g["max"] - g["min"]
    P(f"  {nm}: distancia entre las dos filas de la misma clave -> mediana {dist.median():,.0f} filas | "
      f"adyacentes (distancia 1): {int((dist==1).sum()):,} | min {dist.min():,} | max {dist.max():,}")
    P(f"     posición de la 1ra ocurrencia: filas {g['min'].min():,} a {g['min'].max():,} | "
      f"de la 2da: {g['max'].min():,} a {g['max'].max():,} | total de filas del archivo: {len(df):,}")
    prim = set(g["min"]); ult = set(g["max"])
    P(f"     ¿todas las 2das ocurrencias están al final del archivo? {min(ult) > max(prim)}")

P("\n" + "=" * 105); P("3. ANATOMIA DEL PAR: ¿QUE DIFERENCIA A LAS DOS FILAS?"); P("=" * 105)
def anatomia(nm, df, cols):
    d = df[df.duplicated(K, keep=False)].sort_values(K + ["fila"]).copy()
    d["orden"] = d.groupby(K).cumcount() + 1
    a = d[d["orden"] == 1].set_index(K)[cols]
    b = d[d["orden"] == 2].set_index(K)[cols]
    c0 = cols[0]
    P(f"\n  --- {nm} ---")
    P(f"  Pares idénticos en todas las columnas: {int((a == b).all(axis=1).sum()):,} de {len(a):,}")
    P(f"  1ra > 2da en {c0}: {int((a[c0] > b[c0]).sum()):,} | 1ra < 2da: {int((a[c0] < b[c0]).sum()):,} | iguales: {int((a[c0] == b[c0]).sum()):,}")
    P(f"  -> ¿hay un orden sistemático (una siempre mayor)? {'NO, se reparte' if abs((a[c0] > b[c0]).mean() - .5) < .1 else 'SI'}")
    P(f"  Valores 1ra ocurrencia: media {a[c0].mean():.2f} mediana {a[c0].median():.1f} | 2da: media {b[c0].mean():.2f} mediana {b[c0].median():.1f}")
    P(f"  Correlación entre los dos valores del par: {a[c0].corr(b[c0]):.3f}")
    dif = (a[c0] - b[c0]).abs()
    P(f"  |diferencia|: mediana {dif.median():.1f} | p90 {dif.quantile(.9):.1f} | max {dif.max():.0f} | "
      f"como % del mayor: mediana {(dif / pd.concat([a[c0], b[c0]], axis=1).max(axis=1).replace(0, np.nan)).median():.1%}")
    ceros = ((a[c0] == 0) | (b[c0] == 0))
    P(f"  Pares con un valor en 0: {int(ceros.sum()):,} -> el 0 está en la 1ra: {int((a[c0]==0).sum()):,}, en la 2da: {int((b[c0]==0).sum()):,}, en ambas: {int(((a[c0]==0)&(b[c0]==0)).sum()):,}")
    if len(cols) > 1:
        c1 = cols[1]
        rat_a = (a[c1] / a[c0].replace(0, np.nan)); rat_b = (b[c1] / b[c0].replace(0, np.nan))
        P(f"  Coherencia interna: {c1}/{c0} -> 1ra mediana {rat_a.median():,.0f} | 2da mediana {rat_b.median():,.0f} "
          f"(si son iguales, cada fila es internamente consistente)")
    return a, b

av, bv = anatomia("Ventas", v, ["unidades_vendidas", "venta_neta"])
as_, bs = anatomia("Stock", s, ["stock_disponible", "stock_en_transito"])

P("\n  ¿La 1ra fila de Ventas se corresponde con la 1ra de Stock (mismo 'registro' de origen)?")
jj = av.join(as_, lsuffix="_v1", rsuffix="_s1").join(bv, rsuffix="_v2").join(bs, rsuffix="_s2")
jj.columns = ["u1", "vn1", "sd1", "st1", "u2", "vn2", "sd2", "st2"]
P(f"    corr(unidades 1ra, stock 1ra) = {jj['u1'].corr(jj['sd1']):.3f} | corr(unidades 1ra, stock 2da) = {jj['u1'].corr(jj['sd2']):.3f}")
P(f"    corr(unidades 2da, stock 2da) = {jj['u2'].corr(jj['sd2']):.3f} | corr(unidades 2da, stock 1ra) = {jj['u2'].corr(jj['sd1']):.3f}")
P(f"    casos con venta > stock dentro de la misma posición (1ra-1ra): {int((jj['u1']>jj['sd1']).sum()):,} | cruzado (1ra venta vs 2da stock): {int((jj['u1']>jj['sd2']).sum()):,}")

P("\n  ¿Las dos filas podrían ser una partición (dos proveedores) de un total?")
P(f"    suma del par vs. filas NO duplicadas del mismo SKU y mes en otras tiendas: se compara la media por posición")
noD = v[v["id_producto"].isin(dupsku) & ~v.duplicated(K, keep=False)]
P(f"    filas no duplicadas de esos 15 SKUs: {len(noD):,} (si es 0, el SKU siempre viene duplicado y no hay con qué comparar)")
prom_dup_1ra = av["unidades_vendidas"].mean(); prom_suma = (av["unidades_vendidas"] + bv["unidades_vendidas"]).mean()
prom_resto = v.loc[~v["id_producto"].isin(dupsku), "unidades_vendidas"].mean()
P(f"    unidades promedio: 1ra ocurrencia {prom_dup_1ra:.2f} | suma del par {prom_suma:.2f} | resto del catálogo {prom_resto:.2f}")
P(f"    -> si la suma se pareciera al resto, serían una partición; si la 1ra ya se parece, son registros repetidos")

P("\n" + "=" * 105); P("4. IMPACTO DE CADA CRITERIO DE CONSOLIDACION"); P("=" * 105)
d = v[v.duplicated(K, keep=False)].sort_values(K + ["fila"]).copy(); d["orden"] = d.groupby(K).cumcount() + 1
g = d.groupby(K)
crit_v = pd.DataFrame({
    "1ra ocurrencia (V1 del TP1)": d[d["orden"] == 1].set_index(K)["unidades_vendidas"],
    "2da ocurrencia": d[d["orden"] == 2].set_index(K)["unidades_vendidas"],
    "mayor venta (sugerido por negocio)": g["unidades_vendidas"].max(),
    "menor": g["unidades_vendidas"].min(),
    "promedio": g["unidades_vendidas"].mean(),
    "suma": g["unidades_vendidas"].sum()})
base_u = v.loc[~v["id_producto"].isin(dupsku) | ~v.duplicated(K, keep=False), "unidades_vendidas"].sum()
base_sin_dup = v[~v.duplicated(K, keep=False)]["unidades_vendidas"].sum()
P("  Unidades vendidas totales 2022-2025 según el criterio (resto del dataset = {:,.0f} uds):".format(base_sin_dup))
for c in crit_v.columns:
    tot = base_sin_dup + crit_v[c].sum()
    P(f"    {c:38s} -> {tot:12,.0f} uds   (dif vs 1ra ocurrencia: {tot - (base_sin_dup + crit_v['1ra ocurrencia (V1 del TP1)'].sum()):+,.0f})")
dvn = pd.DataFrame({"1ra": d[d["orden"] == 1].set_index(K)["venta_neta"], "2da": d[d["orden"] == 2].set_index(K)["venta_neta"],
                    "mayor": g["venta_neta"].max(), "suma": g["venta_neta"].sum()})
base_vn = v[~v.duplicated(K, keep=False)]["venta_neta"].sum()
P("\n  Venta neta total ($ M):")
for c in dvn.columns:
    P(f"    {c:8s} -> ${(base_vn + dvn[c].sum())/1e6:10,.1f} M")

ds = s[s.duplicated(K, keep=False)].sort_values(K + ["fila"]).copy(); ds["orden"] = ds.groupby(K).cumcount() + 1
gs = ds.groupby(K)
base_s = s[~s.duplicated(K, keep=False)]
crit_s = {"1ra ocurrencia (V1 del TP1)": ds[ds["orden"] == 1].set_index(K)["stock_disponible"],
          "2da ocurrencia": ds[ds["orden"] == 2].set_index(K)["stock_disponible"],
          "mayor": gs["stock_disponible"].max(), "menor": gs["stock_disponible"].min(),
          "promedio": gs["stock_disponible"].mean(), "suma": gs["stock_disponible"].sum()}
P("\n  Stock total a dic-2025 (unidades) y posiciones con stock > 0:")
for c, ser in crit_s.items():
    ser2 = ser.reset_index(); ser2.columns = K + ["stock_disponible"]
    full = pd.concat([base_s[K + ["stock_disponible"]], ser2])
    dic = full[full["fecha_mes"] == "2025-12-01"]
    P(f"    {c:28s} -> {dic['stock_disponible'].clip(lower=0).sum():9,.0f} uds | posiciones con stock>0: {int((dic['stock_disponible']>0).sum()):,}")

P("\n  Efecto sobre la cobertura de las posiciones afectadas (dic-2025, stock / venta promedio 12m):")
sv = v.copy(); sv["fecha_mes"] = pd.to_datetime(sv["fecha_mes"])
u12 = sv[(sv["fecha_mes"] >= "2025-01-01")].groupby(["id_tienda", "id_producto"])["unidades_vendidas"].mean()
for c, ser in crit_s.items():
    ser2 = ser.reset_index(); ser2.columns = K + ["stock_disponible"]
    full = pd.concat([base_s[K + ["stock_disponible"]], ser2])
    dic = full[(full["fecha_mes"] == "2025-12-01")].set_index(["id_tienda", "id_producto"])
    cov = (dic["stock_disponible"].clip(lower=0) / u12.replace(0, np.nan)).dropna()
    covd = cov[cov.index.get_level_values(1).isin(dupsku)]
    P(f"    {c:28s} -> cobertura mediana global {cov.median():5.2f} meses | de los 15 SKUs afectados {covd.median():5.2f} | "
      f"posiciones >12 meses: {int((cov>12).sum()):,} (de los 15 SKUs: {int((covd>12).sum())})")

P("\n" + "=" * 105); P("5. ¿QUE HIPOTESIS SOBREVIVE?"); P("=" * 105)
aniov = pd.to_datetime(d.loc[d["orden"] == 1, "fecha_mes"]).dt.year.value_counts().sort_index()
P(f"  Duplicados por año: {aniov.to_dict()}")
tot_anio = pd.to_datetime(v["fecha_mes"]).dt.year.value_counts().sort_index()
P(f"  Filas totales por año:   {tot_anio.to_dict()}")
P(f"  % de filas duplicadas sobre el total del año: " +
  str({k: f"{aniov[k]/tot_anio[k]:.2%}" for k in aniov.index}))
P(f"  Meses distintos con duplicados: {d['fecha_mes'].nunique()} de {v['fecha_mes'].nunique()} | tiendas: {d['id_tienda'].nunique()} de 28")
P("  Hipótesis del negocio (Entregable 1): 'migración parcial del reporting en 2024'.")
P("  Contraste: los duplicados aparecen en todos los meses y años, y su peso relativo es estable, no hay salto en 2024.")
P("  Los 15 SKUs duplicados del catálogo difieren SOLO en el proveedor, y son exactamente los que tienen filas repetidas.")
LOG.close()
