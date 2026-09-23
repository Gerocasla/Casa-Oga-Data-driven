# -*- coding: utf-8 -*-
"""
EDA del periodo 2026 (ene-2026 a ago-2026) — Casa Oga, Entregable 2.
Corre sobre Datasets_Normalizados/. No modifica ningun archivo.
Criterio de limpieza V1: dedup exacto + dedup por clave conservando la PRIMERA
ocurrencia + negativos a 0. (Verificado: reproduce las cifras del EDA anterior.)
"""
import pandas as pd, numpy as np, sys, os

sys.stdout.reconfigure(encoding='utf-8')
D = 'Datasets_Normalizados'
K = ['fecha_mes', 'id_tienda', 'id_producto']
CORTE_VIEJO = pd.Timestamp('2025-12-01')

def seccion(t):
    print('\n' + '=' * 78)
    print(t)
    print('=' * 78)

def limpiar(df, clave=K):
    d = df.drop_duplicates()
    d = d.drop_duplicates(clave, keep='first').copy()
    for col in d.select_dtypes(include=[np.number]).columns:
        d[col] = d[col].clip(lower=0)
    return d

# ---------------- carga ----------------
ven = pd.read_csv(f'{D}/Ventas_SKU_tienda_mensual.csv', parse_dates=['fecha_mes'], low_memory=False)
sto = pd.read_csv(f'{D}/Stock_SKU_tienda_mensual.csv', parse_dates=['fecha_mes'], low_memory=False)
cat = pd.read_csv(f'{D}/Productos_catalogo.csv', low_memory=False).drop_duplicates('id_producto', keep='first')
tie = pd.read_csv(f'{D}/Tiendas.csv', low_memory=False)
liq = pd.read_csv(f'{D}/Liquidaciones.csv', low_memory=False)

vl, sl = limpiar(ven), limpiar(sto)
v26 = vl[vl.fecha_mes > CORTE_VIEJO]
s26 = sl[sl.fecha_mes > CORTE_VIEJO]
v25 = vl[vl.fecha_mes.dt.year == 2025]

seccion('1 · PERFIL DEL PERIODO NUEVO')
print(f'  Meses incorporados      : {v26.fecha_mes.nunique()} ({v26.fecha_mes.min():%b-%Y} a {v26.fecha_mes.max():%b-%Y})')
print(f'  Filas de venta (crudas) : {len(ven[ven.fecha_mes > CORTE_VIEJO]):,}')
print(f'  Filas de venta (limpias): {len(v26):,}')
print(f'  Filas de stock (limpias): {len(s26):,}')
print(f'  Tiendas con venta       : {v26.id_tienda.nunique()} de {len(tie)}')
print(f'  SKUs con venta          : {v26[v26.unidades_vendidas > 0].id_producto.nunique()}')
print(f'  Posiciones activas/mes  : min {v26.groupby("fecha_mes").size().min():,} · max {v26.groupby("fecha_mes").size().max():,}')

seccion('2 · VOLUMEN Y COMPARACION CONTRA EL MISMO PERIODO DE 2025')
ini, fin = v26.fecha_mes.min(), v26.fecha_mes.max()
mismos = v25[(v25.fecha_mes.dt.month >= ini.month) & (v25.fecha_mes.dt.month <= fin.month)]
print(f'  {"":22} {"ene-ago 2025":>16} {"ene-ago 2026":>16} {"variacion":>12}')
print('  ' + '-' * 70)
for lbl, col in [('Venta neta ($ M)', 'venta_neta'), ('Unidades', 'unidades_vendidas')]:
    a, b = mismos[col].sum(), v26[col].sum()
    a_, b_ = (a / 1e6, b / 1e6) if 'M' in lbl else (a, b)
    print(f'  {lbl:22} {a_:>16,.1f} {b_:>16,.1f} {100*(b/a-1):>11.1f}%')
pa = mismos.groupby('fecha_mes').size().mean(); pb = v26.groupby('fecha_mes').size().mean()
print(f'  {"Posiciones (prom/mes)":22} {pa:>16,.0f} {pb:>16,.0f} {100*(pb/pa-1):>11.1f}%')
upa = mismos.unidades_vendidas.sum()/len(mismos); upb = v26.unidades_vendidas.sum()/len(v26)
print(f'  {"Unidades por posicion":22} {upa:>16,.2f} {upb:>16,.2f} {100*(upb/upa-1):>11.1f}%')
print(f'  {"Precio medio unidad":22} {mismos.venta_neta.sum()/mismos.unidades_vendidas.sum():>16,.0f} '
      f'{v26.venta_neta.sum()/v26.unidades_vendidas.sum():>16,.0f} '
      f'{100*((v26.venta_neta.sum()/v26.unidades_vendidas.sum())/(mismos.venta_neta.sum()/mismos.unidades_vendidas.sum())-1):>11.1f}%')

seccion('3 · EVOLUCION MENSUAL 2026 (y ultimos meses de 2025 para ver la continuidad)')
ser = vl[vl.fecha_mes >= '2025-09-01'].groupby('fecha_mes').agg(
    posiciones=('unidades_vendidas', 'size'),
    unidades=('unidades_vendidas', 'sum'),
    venta=('venta_neta', 'sum')).reset_index()
ser['u_x_pos'] = ser.unidades / ser.posiciones
print(f'  {"mes":10} {"posiciones":>11} {"unidades":>10} {"venta ($ M)":>13} {"u/posicion":>11}')
print('  ' + '-' * 60)
for _, r in ser.iterrows():
    marca = '  <- corte viejo' if r.fecha_mes == CORTE_VIEJO else ''
    print(f'  {r.fecha_mes:%b-%Y} {r.posiciones:>11,.0f} {r.unidades:>10,.0f} {r.venta/1e6:>13,.1f} {r.u_x_pos:>11.2f}{marca}')

seccion('4 · DISTRIBUCION POR DIMENSIONES EN 2026')
vc = v26.merge(cat[['id_producto', 'categoria']], on='id_producto', how='left')
tot = vc.venta_neta.sum()
print('  Por categoria:')
g = vc.groupby('categoria').venta_neta.sum().sort_values(ascending=False)
m25 = mismos.merge(cat[['id_producto', 'categoria']], on='id_producto', how='left')
g25 = m25.groupby('categoria').venta_neta.sum(); t25 = g25.sum()
for k_, val in g.items():
    print(f'    {k_:16} {100*val/tot:5.1f}%   (mismo periodo 2025: {100*g25.get(k_,0)/t25:5.1f}%)')
vt = v26.merge(tie[['id_tienda', 'region']], on='id_tienda', how='left')
print('  Por region:')
for k_, val in vt.groupby('region').venta_neta.sum().sort_values(ascending=False).items():
    print(f'    {k_:16} {100*val/tot:5.1f}%')

seccion('5 · STOCK Y COBERTURA AL NUEVO CORTE')
ult = s26[s26.fecha_mes == s26.fecha_mes.max()]
ult_v = vl[vl.fecha_mes == s26.fecha_mes.max()]
print(f'  Corte                        : {s26.fecha_mes.max():%b-%Y}')
print(f'  Posiciones con stock > 0     : {(ult.stock_disponible>0).sum():,}   (a dic-2025: 7.993)')
print(f'  Stock total (unidades)       : {ult.stock_disponible.sum():,.0f}')
print(f'  Stock por posicion (mediana) : {ult[ult.stock_disponible>0].stock_disponible.median():.0f}')
u12 = vl[vl.fecha_mes > s26.fecha_mes.max() - pd.DateOffset(months=12)]
cob = ult.stock_disponible.sum() / (u12.unidades_vendidas.sum()/12)
print(f'  Cobertura agregada (12m)     : {cob:.2f} meses   (a dic-2025: ~5,2)')
print(f'  Correlacion unidades vs stock: {v26.merge(s26,on=K).unidades_vendidas.corr(v26.merge(s26,on=K).stock_disponible):.2f}')

seccion('6 · CALIDAD DE DATOS EN EL TRAMO 2026')
c26 = ven[ven.fecha_mes > CORTE_VIEJO]
cs26 = sto[sto.fecha_mes > CORTE_VIEJO]
print(f'  Ventas  · nulos                : {int(c26.isna().sum().sum())}')
print(f'  Ventas  · duplicados exactos   : {int(c26.duplicated().sum())}')
print(f'  Ventas  · duplicados por clave : {int(c26.duplicated(K).sum())}   (2022-2025: 2.378)')
print(f'  Ventas  · unidades negativas   : {int((c26.unidades_vendidas<0).sum())}   (2022-2025: 2.317)')
print(f'  Ventas  · filas en cero        : {int((c26.unidades_vendidas==0).sum())} ({100*(c26.unidades_vendidas==0).mean():.1f}%)   (2022-2025: 19,0%)')
print(f'  Stock   · duplicados por clave : {int(cs26.duplicated(K).sum())}')
print(f'  Stock   · negativos            : {int((cs26.stock_disponible<0).sum())}   (2022-2025: 1.209)')
vs = c26.merge(cs26, on=K, how='inner')
print(f'  Cruce   · venta>0 con stock=0  : {int(((vs.unidades_vendidas>0)&(vs.stock_disponible==0)).sum())}')
print(f'  Cruce   · venta > stock        : {int((vs.unidades_vendidas>vs.stock_disponible).sum())}')

seccion('7 · COBERTURA TEMPORAL DE LAS 15 FUENTES (desalineacion)')
fuentes = {
    'Ventas_SKU_tienda_mensual': 'fecha_mes', 'Stock_SKU_tienda_mensual': 'fecha_mes',
    'Liquidaciones': 'fecha_inicio', 'Devoluciones_SKU': 'fecha',
    'Historial_Precios_SKU': 'fecha_vigencia_desde', 'Ordenes_Compra': 'fecha_pedido',
    'Presupuesto_Ventas_Tienda_Categoria': 'fecha_mes', 'Promociones_Comerciales': 'fecha_inicio',
    'Stock_Deposito_Central': 'fecha_mes', 'Transferencias_Stock': 'fecha_envio',
    'Calendario': 'fecha', 'Productos_catalogo': 'fecha_alta_catalogo',
}
print(f'  {"fuente":38} {"hasta":>12}   {"filas 2026":>12}')
print('  ' + '-' * 68)
sin26 = []
for f, col in fuentes.items():
    d = pd.read_csv(f'{D}/{f}.csv', low_memory=False)
    fe = pd.to_datetime(d[col], errors='coerce')
    n26 = int((fe.dt.year >= 2026).sum())
    if n26 == 0: sin26.append(f)
    ok = f'{n26:,}' if n26 else 'NO  <-- GAP'
    print(f'  {f:38} {fe.max():%Y-%m-%d} {ok:>14}')
print(f'\n  Sin datos en 2026: {", ".join(sin26)}')

seccion('8 · LIQUIDACIONES: REGISTROS NUEVOS')
liq['fi'] = pd.to_datetime(liq.fecha_inicio, errors='coerce')
n = liq[liq.fi.dt.year >= 2026]
print(f'  Total liquidaciones        : {len(liq)}   (EDA anterior: 508)')
print(f'  Con inicio en 2026         : {len(n)}')
print('  Motivos de las nuevas:')
for k_, val in n.motivo.value_counts().items():
    print(f'    {k_:26} {val}')
print(f'  Descuento promedio nuevas  : {n.descuento_pct.mean():.1f}%   (rango {n.descuento_pct.min():.0f}-{n.descuento_pct.max():.0f}%)')
print(f'  Fuera de rango [0,100]     : {int(((n.descuento_pct<0)|(n.descuento_pct>100)).sum())}')

seccion('9 · TOTALES CONSOLIDADOS AL NUEVO CORTE')
print(f'  Venta total 2022 a ago-2026 : ${vl.venta_neta.sum()/1e6:,.1f} M   (al corte dic-2025: $32.538,4 M)')
print(f'  Unidades                    : {vl.unidades_vendidas.sum():,}   (al corte dic-2025: 750.538)')
print(f'  Filas limpias               : {len(vl):,}   (al corte dic-2025: 236.958)')
print('\n  Venta por anio:')
for y, g_ in vl.groupby(vl.fecha_mes.dt.year):
    nota = ' (8 meses)' if y == 2026 else ''
    print(f'    {y}: ${g_.venta_neta.sum()/1e6:>9,.1f} M{nota}')
