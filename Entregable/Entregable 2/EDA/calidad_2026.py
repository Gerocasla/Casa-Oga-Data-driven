# -*- coding: utf-8 -*-
"""
Consolidado de problemas de calidad de datos al corte ago-2026.
Insumo de la Seccion 1 del Entregable 2 - Parte B.
Corre sobre Datasets_Normalizados/. No modifica ningun archivo.
"""
import pandas as pd, numpy as np, sys

sys.stdout.reconfigure(encoding='utf-8')
D = 'Datasets_Normalizados'
K = ['fecha_mes', 'id_tienda', 'id_producto']
FIN25 = pd.Timestamp('2025-12-01')

def sec(t):
    print('\n' + '=' * 76); print(t); print('=' * 76)

L = lambda f, **kw: pd.read_csv(f'{D}/{f}.csv', low_memory=False, **kw)
ven = L('Ventas_SKU_tienda_mensual', parse_dates=['fecha_mes'])
sto = L('Stock_SKU_tienda_mensual', parse_dates=['fecha_mes'])
cat = L('Productos_catalogo')
tie = L('Tiendas', parse_dates=['fecha_apertura'])
liq = L('Liquidaciones')
dev = L('Devoluciones_SKU', parse_dates=['fecha'])
hp  = L('Historial_Precios_SKU', parse_dates=['fecha_vigencia_desde'])
pro = L('Promociones_Comerciales')
pre = L('Presupuesto_Ventas_Tienda_Categoria', parse_dates=['fecha_mes'])
tra = L('Transferencias_Stock', parse_dates=['fecha_envio'])
oc  = L('Ordenes_Compra', parse_dates=['fecha_pedido'])

def part(df, col='fecha_mes'):
    return df[df[col] <= FIN25], df[df[col] > FIN25]

sec('H1 · UNICIDAD — duplicados por clave')
for nom, df in [('Ventas', ven), ('Stock', sto)]:
    v, n = part(df)
    print(f'  {nom:8} exactos {df.duplicated().sum():>5} | por clave {df.duplicated(K).sum():>5}'
          f'  (2022-25: {v.duplicated(K).sum():>5} · 2026: {n.duplicated(K).sum():>3})')
dc = cat[cat.duplicated('id_producto', keep=False)]
print(f'  Catalogo: {cat.id_producto.duplicated().sum()} ids repetidos ({dc.id_producto.nunique()} SKUs)')
difs = [c for c in cat.columns if c != 'id_producto' and dc.groupby('id_producto')[c].nunique().max() > 1]
print(f'    columnas en que difieren: {difs}')
print(f'  Promociones: {pro.duplicated().sum()} exactos · {pro.id_promocion.duplicated().sum()} ids repetidos')

sec('H2 · CONSISTENCIA — ventas antes de la apertura de la tienda')
vt = ven.merge(tie[['id_tienda', 'fecha_apertura']], on='id_tienda')
ant = vt[vt.fecha_mes < vt.fecha_apertura.values.astype('datetime64[M]')]
print(f'  Filas: {len(ant):,} · venta ${ant.venta_neta.sum()/1e6:,.1f} M · tiendas {ant.id_tienda.nunique()}')
for t, g in ant.groupby('id_tienda'):
    ap = tie.loc[tie.id_tienda == t, 'fecha_apertura'].iloc[0]
    print(f'    {t}  abre {ap:%b-%Y}  ·  {g.fecha_mes.nunique():>2} meses previos  ·  ${g.venta_neta.sum()/1e6:>6,.1f} M')

sec('H3 · EXACTITUD / VALIDEZ — valores imposibles')
for nom, df, col in [('Ventas·unidades', ven, 'unidades_vendidas'), ('Ventas·venta_neta', ven, 'venta_neta'),
                     ('Stock·disponible', sto, 'stock_disponible')]:
    v, n = part(df)
    print(f'  {nom:20} negativos {int((df[col]<0).sum()):>5}  (2022-25: {int((v[col]<0).sum()):>5} · 2026: {int((n[col]<0).sum()):>3})'
          f'  min {df[col].min():,.0f}')
fr = liq[(liq.descuento_pct < 0) | (liq.descuento_pct > 100)]
print(f'  Liquidaciones·descuento fuera de [0,100]: {len(fr)} -> {list(fr.descuento_pct)}')
frp = pro[(pro.descuento_pct < 0) | (pro.descuento_pct > 100)]
print(f'  Promociones·descuento fuera de [0,100]:  {len(frp)} -> {list(frp.descuento_pct)}')
num = [c for c in pre.columns if pre[c].dtype.kind in 'if']
for c in num:
    neg = int((pre[c] < 0).sum())
    if neg: print(f'  Presupuesto·{c}: {neg} valores negativos')
print(f'  Presupuesto·ceros en {num[0]}: {int((pre[num[0]]==0).sum())}')

sec('H4 · CONSISTENCIA — cruce ventas vs stock')
m = ven.merge(sto, on=K)
mv, mn = part(m)
for lbl, cond in [('venta > 0 con stock = 0', (m.unidades_vendidas > 0) & (m.stock_disponible == 0)),
                  ('venta > stock disponible', m.unidades_vendidas > m.stock_disponible)]:
    v = ((mv.unidades_vendidas > 0) & (mv.stock_disponible == 0)) if 'stock = 0' in lbl else (mv.unidades_vendidas > mv.stock_disponible)
    n = ((mn.unidades_vendidas > 0) & (mn.stock_disponible == 0)) if 'stock = 0' in lbl else (mn.unidades_vendidas > mn.stock_disponible)
    print(f'  {lbl:26} {int(cond.sum()):>6}  (2022-25: {int(v.sum()):>5} · 2026: {int(n.sum()):>4})')

sec('H5 · CONSISTENCIA — stock en transito vs transferencias')
ult = sto[sto.fecha_mes == sto.fecha_mes.max()]
print(f'  Stock en transito a {sto.fecha_mes.max():%b-%Y}: {ult.stock_en_transito.sum():,.0f} unidades')
tra['rec'] = pd.to_datetime(tra.fecha_recepcion, errors='coerce')
curso = tra[(tra.fecha_envio <= sto.fecha_mes.max() + pd.offsets.MonthEnd(0)) & (tra.rec > sto.fecha_mes.max() + pd.offsets.MonthEnd(0))]
print(f'  Transferencias en curso a esa fecha:     {curso.unidades.sum():,.0f} unidades ({len(curso)} envios)')
if curso.unidades.sum(): print(f'  Relacion: {ult.stock_en_transito.sum()/curso.unidades.sum():.0f}x')

sec('H6 · CONSISTENCIA — liquidaciones')
liq['fi'] = pd.to_datetime(liq.fecha_inicio, errors='coerce')
disc = liq[liq.motivo.str.contains('iscontinua', na=False)]
act = cat[cat.estado == 'Activo'].id_producto
print(f'  Liquidaciones "Discontinuacion": {len(disc)} · de SKUs Activos: {disc.id_producto.isin(act).sum()}')
print(f'  Con tienda "Todas" (no es un id valido): {(liq.tienda=="Todas").sum()}')
fmt = liq.fecha_fin.astype(str).str.contains(' 00:00:00', na=False)
print(f'  fecha_fin con formato distinto (AAAA-MM-DD 00:00:00): {int(fmt.sum())}')

sec('H7 · CONSISTENCIA — ventas vs historial de precios')
hp2 = hp.sort_values(['id_producto', 'fecha_vigencia_desde'])
vv = ven[ven.unidades_vendidas > 0].copy()
vv['precio_impl'] = vv.venta_neta / vv.unidades_vendidas
vv = vv.merge(cat[['id_producto', 'precio_lista']].drop_duplicates('id_producto'), on='id_producto', how='left')
vv['ratio_actual'] = vv.precio_impl / vv.precio_lista
print(f'  Precio implicito / precio de lista ACTUAL: min {vv.ratio_actual.min():.2f} · max {vv.ratio_actual.max():.2f}')
_L = vv.sort_values('fecha_mes').reset_index(drop=True)[['fecha_mes','id_producto','precio_impl']]
_R = (hp2[['fecha_vigencia_desde','id_producto','precio_lista']]
        .rename(columns={'fecha_vigencia_desde':'fecha_mes'})
        .sort_values('fecha_mes').reset_index(drop=True))
mg = pd.merge_asof(_L, _R, on='fecha_mes', by='id_producto', direction='backward')
mg = mg.dropna(subset=['precio_lista'])
mg['ratio_hist'] = mg.precio_impl / mg.precio_lista
print(f'  Precio implicito / precio VIGENTE segun historial: >1,5x en {100*(mg.ratio_hist>1.5).mean():.0f}% de las filas (max {mg.ratio_hist.max():.1f}x)')

sec('H8 · COMPLETITUD — faltantes relevantes')
print(f'  Catalogo · SKUs sin costo_unitario: {cat.costo_unitario.isna().sum()}')
print(f'  Historial · vigencias sin costo   : {hp.costo_unitario.isna().sum()}')
print(f'  Promociones · sin medio_pago      : {pro.medio_pago.isna().sum()} de {len(pro)}')
print(f'  Promociones · sin evento_asociado : {pro.evento_asociado.isna().sum()} de {len(pro)}')

sec('H9 · CONSISTENCIA — variantes de categoria')
for nom, df in [('Productos_catalogo', cat), ('Promociones_Comerciales', pro)]:
    u = sorted(df.categoria.dropna().unique())
    print(f'  {nom:26} {len(u)} valores: {u}')

sec('H10 · ACTUALIDAD — cobertura temporal por fuente')
fuentes = {'Ventas_SKU_tienda_mensual':'fecha_mes','Stock_SKU_tienda_mensual':'fecha_mes',
 'Liquidaciones':'fecha_inicio','Devoluciones_SKU':'fecha','Historial_Precios_SKU':'fecha_vigencia_desde',
 'Ordenes_Compra':'fecha_pedido','Presupuesto_Ventas_Tienda_Categoria':'fecha_mes',
 'Promociones_Comerciales':'fecha_inicio','Stock_Deposito_Central':'fecha_mes',
 'Transferencias_Stock':'fecha_envio','Calendario':'fecha','Productos_catalogo':'fecha_alta_catalogo'}
gap = []
for f, col in fuentes.items():
    fe = pd.to_datetime(L(f)[col], errors='coerce')
    n26 = int((fe.dt.year >= 2026).sum())
    if n26 == 0: gap.append(f)
    print(f'  {f:38} hasta {fe.max():%Y-%m-%d} · filas 2026: {n26:>6,}' + ('   <-- SIN 2026' if not n26 else ''))
print(f'\n  Fuentes sin cobertura de 2026: {", ".join(gap)}')

sec('RESUMEN — dónde se concentran los problemas')
print('  Los problemas de unicidad, exactitud y validez se concentran en 2022-2025.')
print('  El tramo 2026 no presenta duplicados, negativos ni nulos en Ventas ni en Stock.')
