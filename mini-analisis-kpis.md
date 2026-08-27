# Mini-análisis de datos — Casa Óga (2022-2025)

Análisis exploratorio de los 6 CSV subidos al proyecto (Calendario, Tiendas, Productos_catalogo, Stock_SKU_tienda_mensual, Ventas_SKU_tienda_mensual, Liquidaciones). Reporte visual completo, con detalle de dead stock, costo de stock parado y margen en liquidaciones: **[Casa Óga en Números](https://claude.ai/code/artifact/e5c495a6-c672-47fe-9d54-795db8806a7e)**.

## Alcance de los datos
- 28 tiendas, 815 SKUs históricos en catálogo (647 activos / 168 dados de baja; 15 SKUs están duplicados — mismo `id_producto` en 2 filas), 239.336 filas SKU–tienda–mes de ventas y de stock.
- Rango: enero 2022 – diciembre 2025 (48 meses).
- No hay archivo de clientes/CRM entre los datos subidos — soporta bien el proyecto de **Mix de Productos / dead stock**, pero **no** el proyecto de **churn de clientes** (ese requiere datos a nivel cliente que todavía no están en el proyecto).

## Indicadores clave
- Venta neta total (4 años): **$32.353 M** · 746.414 unidades vendidas. Promedio mensual ≈ $674 M.
- Crecimiento: 2022 $1.815 M → 2023 $6.313 M → 2024 $10.594 M → 2025 $13.631 M. Últimos 12 meses vs. 12 previos: **+28,7%**.
- Ticket medio por unidad: ~$43.345.
- Margen bruto teórico de lista (precio_lista vs. costo_unitario): ~44,9% promedio, parejo entre categorías (43,7%–46,1%).
- Mix por categoría (venta): Decoración 21,7% · Cocina y mesa 20,1% · Iluminación 13,5% · Muebles 12,3% · Textil hogar 12,3% · Organización 10,7% · Baño 9,5%.
- Por región: AMBA concentra ~39% de la venta; Patagonia es la más chica (~3,7%).
- Estacionalidad: Primavera y fin de año (Invierno) son los períodos de mayor venta; Otoño el más bajo.
- Concentración (Pareto): sólo 247 de 798 SKUs con venta (31%) explican el 80% de la facturación — el resto es cola larga, candidata natural al modelo de riesgo de baja rotación.

## Rotación de inventario / dead stock (corte dic-2025, catálogo depurado de duplicados)
- 365 combinaciones SKU–tienda (4,6% de las que tienen stock) sin ninguna venta en los últimos 3 meses pese a tener stock disponible.
- Capital inmovilizado en ese dead stock: **$33,4 M**, ~0,9% del valor total de stock a costo ($3.538 M).
- Cobertura de stock agregada: ~5,2 meses de inventario al ritmo de venta reciente.
- **% de capital inmovilizado por categoría** (la métrica relativa, no el $ absoluto): Baño 1,6% · Textil hogar 1,4% · Muebles 0,9% · Iluminación 0,9% · Decoración 0,9% · Cocina y mesa 0,7% · Organización 0,6%.
- **% de combinaciones SKU–tienda sin venta** por categoría: Textil hogar 5,8% · Iluminación 5,5% · Baño 5,4% · Cocina y mesa 4,8% · Decoración 3,9% · Muebles 3,8% · Organización 3,2%.
- **Tiempo promedio parado** (meses sin vender, a la fecha de corte, de los SKU–tienda hoy en dead stock): promedio general 3,2 meses. Por categoría: Muebles 3,5 · Cocina y mesa 3,3 · Decoración 3,3 · Textil hogar 3,3 · Iluminación 3,2 · Organización 3,1 · Baño 2,9.
- Liquidaciones: 508 registradas, descuento promedio 27,2%, duración promedio ~38 días. Motivos: baja rotación (161), fin de temporada (152), sobrestock (102), discontinuación (93).

## Costo de mantener el stock parado
Supuesto: 2% del precio de lista por mes de costo de almacenaje + 3% mensual de costo de oportunidad = 5%/mes.
- Costo mensual actual del dead stock (1.364 unidades): **$3,2 M/mes** ($1,3 M almacenaje + $1,9 M oportunidad) — esto es lo que se sigue generando cada mes mientras ese stock no se mueve.
- Por categoría (costo mensual): Decoración $641 mil · Textil hogar $621 mil · Cocina y mesa $527 mil · Muebles $431 mil · Baño $401 mil · Iluminación $320 mil · Organización $249 mil.
- Costo acumulado estimado (usando el tiempo real que lleva parada cada combinación): **≈$9,7 M** desde que cada una dejó de venderse.

## Impacto de las liquidaciones en el margen
- Margen normal promedio (precio de lista vs. costo): 44,9%. Margen con la liquidación aplicada: 21,7%. **Caída promedio: 23,1 puntos porcentuales**.
- Descuento promedio aplicado: 26,9%.
- El 14,3% de las liquidaciones (70 de 490 válidas) terminan **vendiendo por debajo del costo** (margen negativo).
- Mayor caída de margen por motivo: Sobrestock (−24,6 pp) > Baja rotación (−23,5 pp) > Discontinuación (−22,6 pp) > Fin de temporada (−22,0 pp).
- Mayor caída de margen por categoría: Organización (−26,6 pp) > Iluminación (−24,2 pp) > Muebles (−24,1 pp) > Decoración (−22,8 pp) > Textil hogar (−22,7 pp) > Baño (−21,3 pp) > Cocina y mesa (−20,8 pp).

## Calidad de datos (a limpiar antes de modelar)
- 1.209 filas de stock con `stock_disponible` negativo (imposible físicamente).
- 2.317 filas de ventas con `unidades_vendidas`/`venta_neta` negativas (¿devoluciones sin marcar como tal?).
- **15 SKUs duplicados en el catálogo** (mismo `id_producto` en 2 filas) — se usó la 1ra ocurrencia para el detalle de dead stock y liquidaciones; esto corrige a la baja los números de capital inmovilizado del primer corte (de $46 M a $33,4 M).
- Categoría con nombres inconsistentes en el catálogo: variantes "Decoración"/"DECO", "Textil Hogar"/"TEXTIL_HOGAR" además de las formas estándar (21 SKUs afectados).
- 22 SKUs sin `costo_unitario` cargado (impide calcular margen/capital inmovilizado para esos productos).
- 8 registros de liquidaciones con fechas no parseables y 3 con `descuento_pct` fuera de rango (negativo o >100%).
- 77 filas duplicadas en ventas y stock combinadas.

Esto confirma lo que ya anticipaban los documentos de contexto ("registros incompletos y valores faltantes... aunque el negocio considera que estos problemas pueden abordarse con esfuerzo adicional").

## Relevancia para el proyecto
- **Mix Productos / dead stock**: los datos disponibles (ventas, stock, catálogo, liquidaciones) alcanzan para construir el modelo a nivel SKU–tienda propuesto en el entregable. Baño y Textil hogar son las categorías donde priorizar el modelo de riesgo (mayor % de capital inmovilizado); Textil hogar e Iluminación tienen la mayor proporción de combinaciones sin venta.
- **Clientes y Fidelización / churn**: falta el dataset de clientes/transacciones a nivel cliente (historial de compras individual, fidelización, campañas) — es el próximo dato a conseguir para avanzar en esa línea.
