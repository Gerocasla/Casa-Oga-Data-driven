# -*- coding: utf-8 -*-
"""
Factor de ajuste del costo de orden de compra para los 22 SKUs sin costo en catalogo.

Criterio definido por el negocio (respuestas P3-P7, ronda 2):
  - El costo de la OC no es el mismo concepto que el costo de catalogo: usado tal cual,
    da un margen de ~55% contra ~45% del resto del catalogo.
  - Calcular el factor implicito que nivela el margen de estos 22 SKUs con el del resto:
        factor = (costo_catalogo / precio_lista) promedio del resto
                 ---------------------------------------------------
                 (costo_OC       / precio_lista) promedio de los 22
  - costo_ajustado = costo_OC x factor
  - ES UN SUPUESTO DEL PROYECTO, NO UN DATO DEL NEGOCIO. Declararlo como tal.

Costo OC por SKU: promedio ponderado por unidades de todas sus ordenes de compra.
Salida: resultados/costo_ajustado_22_skus.csv y resultados/factor_costo_oc_log.txt
"""
import os, sys
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "..", "..", "Datasets_Normalizados")
OUT = os.path.join(BASE, "resultados")
LOG = open(os.path.join(OUT, "factor_costo_oc_log.txt"), "w", encoding="utf-8")
def P(*a):
    t = " ".join(str(x) for x in a); print(t); LOG.write(t + "\n")

cat = pd.read_csv(os.path.join(DATA, "Productos_catalogo.csv")).drop_duplicates("id_producto")
oc  = pd.read_csv(os.path.join(DATA, "Ordenes_Compra.csv"))
sto = pd.read_csv(os.path.join(DATA, "Stock_SKU_tienda_mensual.csv"), parse_dates=["fecha_mes"])

# costo OC ponderado por unidades, por SKU
oc["monto"] = oc.unidades * oc.costo_unitario_ars
ocs = oc.groupby("id_producto").agg(monto=("monto", "sum"), uds=("unidades", "sum"),
                                     n_oc=("id_oc", "size"),
                                     oc_mediana=("costo_unitario_ars", "median"))
ocs["costo_oc"] = ocs.monto / ocs.uds

cat = cat.merge(ocs[["costo_oc", "oc_mediana", "n_oc"]], on="id_producto", how="left")
sin = cat[cat.costo_unitario.isna()].copy()
con = cat[cat.costo_unitario.notna()].copy()

P("=" * 78); P("FACTOR DE AJUSTE DEL COSTO DE OC — 22 SKUs sin costo en catalogo"); P("=" * 78)
P(f"SKUs sin costo en catalogo      : {len(sin)}")
P(f"  con ordenes de compra          : {sin.costo_oc.notna().sum()}  (OCs: {int(sin.n_oc.sum())})")

# relacion costo/precio
con["r"] = con.costo_unitario / con.precio_lista
sin["r"] = sin.costo_oc / sin.precio_lista
r_resto, r_22 = con.r.mean(), sin.r.mean()
P("\n--- Relacion costo / precio de lista ---")
P(f"  Resto del catalogo (costo catalogo): {r_resto:.4f}  -> margen {100*(1-r_resto):.1f}%")
P(f"  22 SKUs (costo OC sin ajustar)     : {r_22:.4f}  -> margen {100*(1-r_22):.1f}%")

factor = r_resto / r_22
sin["costo_ajustado"] = sin.costo_oc * factor
m_aj = 1 - (sin.costo_ajustado / sin.precio_lista).mean()
P(f"\n  FACTOR = {r_resto:.4f} / {r_22:.4f} = {factor:.4f}  (+{100*(factor-1):.1f}% sobre el costo de OC)")
P(f"  Margen de los 22 con costo ajustado: {100*m_aj:.1f}%  (objetivo: {100*(1-r_resto):.1f}%)")

# control: en el resto, ¿el costo de OC coincide con el de catalogo?
ctrl = con[con.costo_oc.notna()]
q = ctrl.costo_oc / ctrl.costo_unitario
P("\n--- Control: costo OC / costo catalogo en el resto de los SKUs ---")
P(f"  SKUs comparables: {len(ctrl)} · mediana {q.median():.3f} · p10 {q.quantile(.1):.3f} · p90 {q.quantile(.9):.3f}")
P("  (Si en el resto la OC ~ catalogo, la brecha de los 22 es propia de esos productos.)")

# sensibilidad al criterio de costo OC
alt = 1 - (sin.oc_mediana * (r_resto / (sin.oc_mediana / sin.precio_lista).mean()) / sin.precio_lista).mean()
fac_med = r_resto / (sin.oc_mediana / sin.precio_lista).mean()
P("\n--- Sensibilidad ---")
P(f"  Con mediana de OC en vez de ponderado: factor {fac_med:.4f}")

# por categoria (solo informativo)
P("\n--- Distribucion de los 22 por categoria ---")
for k, g in sin.groupby("categoria"):
    P(f"  {k:14} {len(g):>2} SKUs · margen OC sin ajustar {100*(1-g.r.mean()):.1f}%")

# impacto en capital inmovilizado (stock al ultimo corte, a costo)
corte = sto.fecha_mes.max()
st = (sto[sto.fecha_mes == corte].drop_duplicates(["fecha_mes", "id_tienda", "id_producto"])
      .assign(stock=lambda d: d.stock_disponible.clip(lower=0))
      .groupby("id_producto").stock.sum())
sin["stock"] = sin.id_producto.map(st).fillna(0)
med_cat = con.groupby("categoria").costo_unitario.median()
sin["costo_mediana_cat"] = sin.categoria.map(med_cat)
P(f"\n--- Valor del stock de los 22 SKUs a {corte:%b-%Y} ({int(sin.stock.sum()):,} unidades) ---")
for lbl, col in [("Mediana de categoria (criterio anterior)", "costo_mediana_cat"),
                 ("Costo OC sin ajustar", "costo_oc"),
                 ("Costo OC ajustado (criterio adoptado)", "costo_ajustado")]:
    P(f"  {lbl:42} ${(sin.stock*sin[col]).sum()/1e6:>7,.2f} M")

sin[["id_producto", "categoria", "precio_lista", "costo_oc", "costo_ajustado", "costo_mediana_cat", "n_oc"]] \
    .round(2).to_csv(os.path.join(OUT, "costo_ajustado_22_skus.csv"), index=False)
P("\nGuardado: resultados/costo_ajustado_22_skus.csv")
LOG.close()
