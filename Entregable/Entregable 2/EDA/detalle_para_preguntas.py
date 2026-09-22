"""Detalle fino de los casos que van a la ronda de preguntas al negocio."""
import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(BASE, "..", "..", "..", "Datasets"))
RES = os.path.join(BASE, "resultados")
LOG = open(os.path.join(RES, "detalle_para_preguntas_log.txt"), "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n")
rd = lambda n: pd.read_csv(os.path.join(DATA, n + ".csv"))
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.max_rows", 60)

cat = rd("Productos_catalogo"); hp = rd("Historial_Precios_SKU"); oc = rd("Ordenes_Compra")
v = rd("Ventas_SKU_tienda_mensual"); s = rd("Stock_SKU_tienda_mensual"); liq = rd("Liquidaciones")
pm = rd("Promociones_Comerciales"); pr = rd("Presupuesto_Ventas_Tienda_Categoria"); dev = rd("Devoluciones_SKU")
tiendas = rd("Tiendas")
K = ["fecha_mes", "id_tienda", "id_producto"]

P("=" * 100); P("1. LOS 22 SKUs SIN COSTO UNITARIO"); P("=" * 100)
sin = cat[cat["costo_unitario"].isna()].copy()
ocg = oc.groupby("id_producto").agg(ocs=("id_oc", "count"), costo_min=("costo_unitario_ars", "min"),
                                    costo_max=("costo_unitario_ars", "max"), costo_ult=("costo_unitario_ars", "last"),
                                    ult_pedido=("fecha_pedido", "max"), uds=("unidades", "sum"))
ocw = oc.assign(t=oc["unidades"] * oc["costo_unitario_ars"]).groupby("id_producto").apply(lambda x: x["t"].sum() / x["unidades"].sum())
stock_dic = s[s["fecha_mes"] == "2025-12-01"].groupby("id_producto")["stock_disponible"].sum()
pos_dic = s[(s["fecha_mes"] == "2025-12-01") & (s["stock_disponible"] > 0)].groupby("id_producto")["id_tienda"].nunique()
ven = v.groupby("id_producto").agg(venta=("venta_neta", "sum"), uds_vend=("unidades_vendidas", "sum"))
t = sin[["id_producto", "categoria", "subcategoria", "proveedor", "precio_lista", "estado", "fecha_alta_catalogo"]].set_index("id_producto")
t = t.join(ocg).join(ocw.rename("costo_ponderado_oc")).join(stock_dic.rename("stock_dic25")).join(pos_dic.rename("tiendas_con_stock")).join(ven)
t["margen_si_uso_oc_%"] = ((t["precio_lista"] - t["costo_ponderado_oc"]) / t["precio_lista"] * 100).round(1)
t["dispersion_costo_oc_%"] = ((t["costo_max"] - t["costo_min"]) / t["costo_min"] * 100).round(1)
P(t.round(0).to_string())
t.round(2).to_csv(os.path.join(RES, "skus_sin_costo.csv"), encoding="utf-8-sig")
P(f"\n  Resumen: {len(sin)} SKUs | categorias: {sin['categoria'].value_counts().to_dict()}")
P(f"  Estado: {sin['estado'].value_counts().to_dict()} | altas {sin['fecha_alta_catalogo'].min()} a {sin['fecha_alta_catalogo'].max()}")
P(f"  Stock a dic-2025: {t['stock_dic25'].sum():,.0f} unidades en {t['tiendas_con_stock'].sum():,.0f} posiciones SKU-tienda")
P(f"  Venta acumulada de estos SKUs: ${t['venta'].sum()/1e6:,.1f} M ({t['venta'].sum()/v['venta_neta'].sum():.2%} del total)")
P(f"  Valuacion del stock dic-25 con costo ponderado de OC: ${(t['stock_dic25']*t['costo_ponderado_oc']).sum()/1e6:,.1f} M")
med_cat = cat.assign(c=cat["categoria"].replace({"Decoración": "Decoracion", "DECO": "Decoracion", "Textil Hogar": "Textil hogar", "TEXTIL_HOGAR": "Textil hogar"})).groupby("c")["costo_unitario"].median()
t["costo_mediana_categoria"] = t["categoria"].replace({"Decoración": "Decoracion", "DECO": "Decoracion", "Textil Hogar": "Textil hogar", "TEXTIL_HOGAR": "Textil hogar"}).map(med_cat)
t["dif_oc_vs_mediana_%"] = ((t["costo_ponderado_oc"] - t["costo_mediana_categoria"]) / t["costo_mediana_categoria"] * 100).round(1)
P(f"  Criterio TP1 (mediana de categoria) vs costo real de OC: diferencia mediana {t['dif_oc_vs_mediana_%'].median():.1f}%, "
  f"rango {t['dif_oc_vs_mediana_%'].min():.1f}% a {t['dif_oc_vs_mediana_%'].max():.1f}%")
P(f"  Valuacion del stock con mediana de categoria: ${(t['stock_dic25']*t['costo_mediana_categoria']).sum()/1e6:,.1f} M "
  f"(vs ${(t['stock_dic25']*t['costo_ponderado_oc']).sum()/1e6:,.1f} M con costo de OC)")
P(f"  Margen de lista implicito usando costo de OC: {t['margen_si_uso_oc_%'].min():.1f}% a {t['margen_si_uso_oc_%'].max():.1f}% "
  f"(mediana {t['margen_si_uso_oc_%'].median():.1f}%) | margen del resto del catalogo: "
  f"{((cat['precio_lista']-cat['costo_unitario'])/cat['precio_lista']*100).median():.1f}%")
P(f"  Dispersion de costo entre OCs del mismo SKU: mediana {t['dispersion_costo_oc_%'].median():.1f}%, max {t['dispersion_costo_oc_%'].max():.1f}%")

P("\n" + "=" * 100); P("2. HISTORIAL DE PRECIOS: COSTO NULO"); P("=" * 100)
nul = hp[hp["costo_unitario"].isna()]
P(f"  {len(nul)} filas, {nul['id_producto'].nunique()} SKUs | ¿son los mismos 22 del catalogo? {set(nul['id_producto'])==set(sin['id_producto'])}")
P(f"  Vigencias por SKU: {nul.groupby('id_producto').size().value_counts().to_dict()}")
P(f"  ¿Algun SKU tiene costo en una vigencia y nulo en otra? "
  f"{int(hp.groupby('id_producto')['costo_unitario'].apply(lambda x: x.isna().any() and x.notna().any()).sum())}")
P(f"  Precio de lista de esas filas: nulos {int(nul['precio_lista'].isna().sum())} (o sea: falta el costo pero NO el precio)")
P("  Detalle:\n" + nul.to_string(index=False))
P(f"\n  Control general del historial: {len(hp)} filas / {hp['id_producto'].nunique()} SKUs; ultima vigencia = catalogo en 800/800 precios; "
  f"primera vigencia = fecha_alta en 800/800; sin solapamientos ni huecos")
P(f"  Vigencias con fecha de inicio posterior a dic-2025: {int((pd.to_datetime(hp['fecha_vigencia_desde'])>'2025-12-31').sum())}")
P(f"  Saltos de precio entre vigencias consecutivas (%): " +
  str(hp.sort_values(['id_producto','fecha_vigencia_desde']).groupby('id_producto')['precio_lista'].pct_change().mul(100).describe(percentiles=[.05,.5,.95]).round(1).to_dict()))

P("\n" + "=" * 100); P("3. OUTLIERS / VALORES IMPOSIBLES"); P("=" * 100)
P("\n3.1 Stock negativo")
neg = s[s["stock_disponible"] < 0].copy()
P(f"  {len(neg):,} filas | min {neg['stock_disponible'].min()} | mediana {neg['stock_disponible'].median()} | suma {neg['stock_disponible'].sum():,}")
P(f"  Por anio: {pd.to_datetime(neg['fecha_mes']).dt.year.value_counts().sort_index().to_dict()}")
P(f"  SKUs afectados: {neg['id_producto'].nunique()} | tiendas: {neg['id_tienda'].nunique()} de 28 | "
  f"posiciones SKU-tienda distintas: {neg.groupby(['id_tienda','id_producto']).ngroups:,}")
P(f"  Concentracion: top 5 tiendas {neg['id_tienda'].value_counts().head().to_dict()}")
P(f"  Tamanio: |stock| > 50 en {int((neg['stock_disponible']<-50).sum())} filas, > 100 en {int((neg['stock_disponible']<-100).sum())}")
vn = v.merge(neg[K + ["stock_disponible"]], on=K)
P(f"  De esas filas, con venta > 0 el mismo mes: {int((vn['unidades_vendidas']>0).sum()):,} ({(vn['unidades_vendidas']>0).mean():.1%}) "
  f"| unidades vendidas mediana {vn['unidades_vendidas'].median():.0f}")
P(f"  ¿El faltante se parece a la venta del mes? |stock_neg| vs unidades vendidas: correlacion {vn['stock_disponible'].abs().corr(vn['unidades_vendidas']):.3f} | "
  f"|stock_neg| mediana {vn['stock_disponible'].abs().median():.0f}")
sq = s.sort_values(K[2:] + ["fecha_mes"]).copy()
sq["sig"] = sq.groupby(["id_tienda", "id_producto"])["stock_disponible"].shift(-1)
nn = sq[sq["stock_disponible"] < 0]
P(f"  Mes siguiente de una posicion con stock negativo: vuelve a positivo en {int((nn['sig']>0).sum()):,} casos, "
  f"sigue negativo en {int((nn['sig']<0).sum()):,}, sin dato en {int(nn['sig'].isna().sum()):,}")

P("\n3.2 Ventas y venta_neta negativas (= devoluciones)")
negv = v[v["unidades_vendidas"] < 0]
P(f"  {len(negv):,} filas | unidades {negv['unidades_vendidas'].sum():,} | monto ${negv['venta_neta'].sum()/1e6:,.1f} M | "
  f"coinciden 1 a 1 con Devoluciones_SKU (misma clave y mismas unidades)")
P(f"  Motivos (registros/unidades): " + str(dev.groupby("motivo")["unidades_devueltas"].agg(["count", "sum"]).to_dict("index")))
P(f"  Peso: {abs(negv['unidades_vendidas'].sum())/v.loc[v['unidades_vendidas']>0,'unidades_vendidas'].sum():.2%} de las unidades vendidas")
P(f"  ¿La misma clave tiene tambien una fila de venta positiva ese mes? "
  f"{int(negv.merge(v[v['unidades_vendidas']>0][K], on=K, how='inner').shape[0]):,} de {len(negv):,}")

P("\n3.3 Descuentos fuera de rango")
P("  Liquidaciones:\n" + liq[(liq["descuento_pct"] < 0) | (liq["descuento_pct"] > 100)].to_string(index=False))
P("  Promociones:\n" + pm[(pm["descuento_pct"] < 0) | (pm["descuento_pct"] > 100)].to_string(index=False))
P(f"  Valores validos de descuento en liquidaciones: {sorted(liq.loc[(liq['descuento_pct']>=0)&(liq['descuento_pct']<=100),'descuento_pct'].unique())}")
P(f"  Valores validos en promociones: {sorted(pm.loc[(pm['descuento_pct']>=0)&(pm['descuento_pct']<=100),'descuento_pct'].unique())}")

P("\n3.4 Presupuesto negativo y en cero")
P("  Negativos:\n" + pr[(pr["presupuesto_venta_ars"] < 0) | (pr["presupuesto_unidades"] < 0)].to_string(index=False))
z = pr[pr["presupuesto_venta_ars"] == 0]
P(f"  Ceros: {len(z)} filas, meses {sorted(z['fecha_mes'].unique())} | tiendas afectadas {z['id_tienda'].nunique()} de 28")
P(f"  Presupuesto medio por celda en 2022: ${pr[pr['fecha_mes'].str[:4]=='2022']['presupuesto_venta_ars'].mean():,.0f}")
LOG.close()
