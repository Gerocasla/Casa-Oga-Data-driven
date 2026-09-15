# Mini-análisis de datos — Casa Óga (2022-2025)

Análisis exploratorio de los 6 CSV subidos al proyecto (Calendario, Tiendas, Productos_catalogo, Stock_SKU_tienda_mensual, Ventas_SKU_tienda_mensual, Liquidaciones), más las respuestas oficiales del relevamiento a la empresa (Grupo 1). Reporte visual completo: **[Casa Óga en Números](https://claude.ai/code/artifact/e5c495a6-c672-47fe-9d54-795db8806a7e)**. Evolución mensual del % de stock vendido por categoría: **[Histórico % vendido](https://claude.ai/code/artifact/851f10a1-61a4-4156-befb-158561905139)**. Dashboard de diagnóstico de dead stock y propuesta de sistema predictivo (pensado para presentar a dirección): **[Dead Stock — Diagnóstico y Predictivo](https://claude.ai/code/artifact/d360de71-73a6-43a5-80c5-d099da6233b6)**.

## Alcance de los datos
- 28 tiendas, 815 SKUs históricos en catálogo (647 activos / 168 dados de baja; 15 SKUs están duplicados — mismo `id_producto` en 2 filas), 239.336 filas SKU–tienda–mes de ventas y de stock.
- Rango: enero 2022 – diciembre 2025 (48 meses).
- El catálogo trae `fecha_alta_catalogo`, `fecha_baja_catalogo` y `estado` (Activo/Discontinuado) por SKU — se usan para el modelo de dead stock (antigüedad real de cada combinación SKU–tienda y detección de productos discontinuados con stock remanente).
- No hay archivo de clientes/CRM entre los datos subidos — soporta bien el proyecto de **Mix de Productos / dead stock**, pero **no** el proyecto de **churn de clientes** (ese requiere datos a nivel cliente que todavía no están en el proyecto).
- El relevamiento oficial (Grupo 1) confirmó que **no existe una definición formal de dead stock** en la empresa hoy — la desarrollamos nosotros a partir de los datos, y el proyecto es justamente proponerla. También mencionan un `Proveedores.csv` (lead time, lote mínimo, condiciones de devolución por proveedor) como "ya entregado", pero **ese archivo no está entre los que tenemos** — es un dato pendiente de reclamar.

## Indicadores clave
- Venta neta total (4 años): **$32.353 M** · 746.414 unidades vendidas. Promedio mensual ≈ $674 M.
- Crecimiento: 2022 $1.815 M → 2023 $6.313 M → 2024 $10.594 M → 2025 $13.631 M. Últimos 12 meses vs. 12 previos: **+28,7%**.
- Ticket medio por unidad: ~$43.345.
- Margen bruto teórico de lista (precio_lista vs. costo_unitario): ~44,9% promedio, parejo entre categorías (43,7%–46,1%).
- Mix por categoría (venta): Decoración 21,7% · Cocina y mesa 20,1% · Iluminación 13,5% · Muebles 12,3% · Textil hogar 12,3% · Organización 10,7% · Baño 9,5%.
- Por región: AMBA concentra ~39% de la venta; Patagonia es la más chica (~3,7%).
- Estacionalidad: **todas las categorías** muestran el mismo patrón — pico en noviembre-diciembre, piso en enero-febrero. A nivel subcategoría (25 en total) el patrón es prácticamente idéntico en casi todas, lo que sugiere un efecto dominante de "temporada de regalos/fin de año" más que estacionalidades propias de cada tipo de producto (por ej. el ciclo invierno/verano de blanquería que el negocio menciona informalmente para Textil hogar no aparece diferenciado en los datos). Vale la pena confirmar esto con el negocio, ya que es un dataset armado para el curso y podría no capturar esas diferencias.
- Concentración (Pareto): sólo 247 de 798 SKUs con venta (31%) explican el 80% de la facturación — el resto es cola larga, candidata natural al modelo de riesgo de baja rotación.

## Dead stock: metodología final

Definimos una combinación **SKU–tienda** como dead stock (al mes de corte, con `stock_disponible > 0`) si se cumple **cualquiera** de estas tres condiciones:

1. **`meses_sin_venta ≥ 3`** — no vendió nada en los últimos 3 meses consecutivos (mirando hacia atrás desde el corte, sobre la grilla mensual completa, no solo las filas presentes).
2. **`stock_muerto_proyectado > 0`** — el stock actual excede lo que se vendería en los próximos 12 meses al ritmo de venta reciente. Se calcula como `run_rate = ventas de los últimos 12 meses ÷ meses reales que esa combinación SKU–tienda lleva con datos (tope 12)`, y luego `stock_muerto_proyectado = máx(0, stock_disponible − run_rate × 12)`. Esta condición captura el caso que el binario de "0 ventas" se pierde: un producto que vende poco pero tiene semejante stock encima que, aunque siga vendiendo al mismo ritmo, no lo va a terminar de rotar en un año.
3. **Discontinuado con stock** — `estado = Discontinuado` y todavía tiene stock disponible. Si el negocio ya decidió no reponerlo, ese stock es candidato a liquidación por definición, más allá de cómo esté vendiendo.

Elegimos el **OR** (cualquiera de las tres) en vez del AND: probamos ambas versiones y con AND (las tres condiciones a la vez) el universo cae a menos del 1% del catálogo porque exige que además de no haber vendido nada, el stock también sea estructuralmente excedente — y eso deja afuera justo el caso de "vende poco pero tiene demasiado stock" que queríamos capturar.

Esta definición reemplaza la versión anterior de este documento, que solo usaba la condición 1 (365 combinaciones, 4,6%). La ampliación con las condiciones 2 y 3 casi duplica la cobertura del problema real sin inflarlo artificialmente por productos nuevos (el `run_rate` se ajusta por la antigüedad real de cada combinación SKU–tienda, no por la del producto en general).

## Dead stock: resultado (corte dic-2025)
- **431 combinaciones SKU–tienda en dead stock, 5,39% de las 7.993 que tienen stock** (la definición anterior, que solo miraba 0-ventas en 3 meses, daba 4,6% — la nueva definición combinada suma los casos de sobrestock estructural y discontinuados).
- **Capital inmovilizado: $34,2 M** (valuado a costo: stock completo para las que no vendieron nada o están discontinuadas, solo el excedente proyectado para las que venden pero exceden 12 meses de cobertura). Es ~0,97% del valor total de stock a costo.
- **Costo de mantenerlo: $3,15 M/mes** (2% almacenaje + 3% costo de oportunidad, sobre precio de lista de las unidades en dead stock — este es el costo mensual recurrente mientras ese stock no se mueva).
- **Por categoría** (% de combinaciones en dead stock, hoy vs. hace 12 meses): Textil hogar 6,49% (era 5,75%, empeoró) · Baño 6,03% (era 7,01%, mejoró) · Cocina y mesa 5,61% (era 7,41%, mejoró) · Iluminación 5,51% (era 7,02%, mejoró) · Muebles 5,13% (era 5,79%, mejoró) · Decoración 4,77% (era 4,30%, empeoró) · Organización 4,31% (era 6,99%, mejoró).

## Evolución en el tiempo (ene-2023 a dic-2025)
- **En % del catálogo, el problema mejoró**: de 9,15% en ene-23 a 5,39% en dic-25 (promedio de los últimos 12 meses: 5,71%). La mejora relativa se explica porque el negocio (y el catálogo activo) creció más rápido que el stock parado, no porque el problema haya desaparecido.
- **En pesos, el problema creció y es volátil**: promedió $27,6 M en 2023 contra $40,7 M en los últimos 12 meses, con un pico de **$51,1 M en agosto de 2024** — el momento más alto en 3 años. El costo mensual de mantenimiento acompaña esa volatilidad, promediando $3,74 M/mes en el último año.
- Esta es la base del pedido al negocio: si el % viene mejorando pero el $ sigue creciendo y con picos grandes, un sistema que detecte antes (antes de que el stock llegue a "no vendió nada en 3 meses") puede achatar esos picos y evitar que el capital vuelva a treparse.

## Umbral de "semáforo" propuesto por el negocio (validación)
El relevamiento menciona que el negocio pensaba en un semáforo de rotación mensual: Rojo <30%, Amarillo 30-70%, Verde >70% (unidades vendidas ÷ stock disponible, por mes). Lo corrimos sobre los datos reales: con ese umbral literal, **73,6% del catálogo queda en Rojo** — muy por encima de la capacidad operativa que el propio negocio dijo tener para actuar sobre alertas (entre 420 y 700 SKU–tienda por mes). El umbral tal cual está planteado no es accionable. Alternativas que evaluamos: umbral relativo a la mediana de cada categoría (Rojo = tasa de venta menor al 50% de la mediana de su categoría), o directamente la definición de dead stock de este documento, que ya viene calibrada empíricamente. Recomendamos validar el umbral final con el negocio antes de fijarlo.

## Costo de mantener el stock parado
Supuesto (confirmado con el negocio): 2% del precio de lista por mes de costo de almacenaje + 3% mensual de costo de oportunidad = 5%/mes, aplicado sobre las unidades en dead stock (stock completo si no vendió nada o está discontinuado; solo el excedente proyectado si es por sobrestock estructural).
- Costo mensual actual (dic-2025): **$3,15 M/mes**. Promedio de los últimos 12 meses: **$3,74 M/mes**.
- Por categoría (costo mensual, dic-2025): Decoración $705 mil · Textil hogar $548 mil · Cocina y mesa $500 mil · Muebles $434 mil · Baño $341 mil · Organización $329 mil · Iluminación $295 mil.

## Impacto de las liquidaciones en el margen
- Margen normal promedio (precio de lista vs. costo): 44,9%. Margen con la liquidación aplicada: 21,7%. **Caída promedio: 23,1 puntos porcentuales**.
- Descuento promedio aplicado: 26,9%.
- El 14,3% de las liquidaciones (70 de 490 válidas) terminan **vendiendo por debajo del costo** (margen negativo).
- Mayor caída de margen por motivo: Sobrestock (−24,6 pp) > Baja rotación (−23,5 pp) > Discontinuación (−22,6 pp) > Fin de temporada (−22,0 pp).
- Mayor caída de margen por categoría: Organización (−26,6 pp) > Iluminación (−24,2 pp) > Muebles (−24,1 pp) > Decoración (−22,8 pp) > Textil hogar (−22,7 pp) > Baño (−21,3 pp) > Cocina y mesa (−20,8 pp).
- Esta es la base del argumento de negocio para el sistema predictivo: detectar antes permite liquidar antes, con menos descuento — hoy se llega tarde y el margen se resiente fuerte.

## Compras y reposición (relevamiento oficial)
No hay una frecuencia de compra/reposición formal documentada. El circuito para productos nuevos es informal: el equipo de Compras y Categorías propone en base a tendencias de mercado y desempeño de proveedores existentes; la aprobación es entre Compras y Comercial, sin comité formal; la cantidad inicial de compra se define por el mínimo de pedido del proveedor + una estimación manual de demanda (no un modelo); la asignación a tiendas también es manual (todas por default, con excepciones por tamaño de local). El `Proveedores.csv` (lead time, lote mínimo, condiciones de devolución) que permitiría estimar una cadencia real de reposición está marcado como entregado en el relevamiento pero no está disponible entre los archivos del proyecto — pendiente de reclamar.

## Transferencias entre tiendas
El relevamiento no describe un proceso sistemático de transferencia de stock entre tiendas o con depósito central hoy. Se envió un pedido formal a Gerencia de Operaciones solicitando el historial de transferencias (si existe) para poder incorporarlo como palanca de acción del sistema predictivo (mover stock excedente a una tienda con mejor rotación, en vez de liquidar).

## Calidad de datos (a limpiar antes de modelar)
- 1.209 filas de stock con `stock_disponible` negativo (imposible físicamente).
- 2.317 filas de ventas con `unidades_vendidas`/`venta_neta` negativas (¿devoluciones sin marcar como tal?).
- **15 SKUs duplicados en el catálogo** (mismo `id_producto` en 2 filas) — se usó la 1ra ocurrencia para todo el análisis; esto corrige a la baja los números de capital inmovilizado del primer corte (de $46 M a valores consistentes con el resto del documento).
- Categoría con nombres inconsistentes en el catálogo: variantes "Decoración"/"DECO", "Textil Hogar"/"TEXTIL_HOGAR" además de las formas estándar (21 SKUs afectados).
- 22 SKUs sin `costo_unitario` cargado (impide calcular margen/capital inmovilizado para esos productos).
- 8 registros de liquidaciones con fechas no parseables y 3 con `descuento_pct` fuera de rango (negativo o >100%).
- 77 filas duplicadas en ventas y stock combinadas.

Esto confirma lo que ya anticipaban los documentos de contexto ("registros incompletos y valores faltantes... aunque el negocio considera que estos problemas pueden abordarse con esfuerzo adicional").

## Relevancia para el proyecto
- **Mix Productos / dead stock**: los datos disponibles (ventas, stock, catálogo, liquidaciones) alcanzan para construir el modelo a nivel SKU–tienda propuesto en el entregable, y ya tenemos una definición de dead stock calibrada y validada contra el semáforo propuesto por el negocio. El paso siguiente es formalizar el sistema predictivo (alertas mensuales por combinación SKU–tienda) y conseguir el dato de transferencias y el `Proveedores.csv` para poder recomendar acciones concretas (reponer distinto, transferir, liquidar) y no solo detectar el problema.
- **Clientes y Fidelización / churn**: falta el dataset de clientes/transacciones a nivel cliente (historial de compras individual, fidelización, campañas) — es el próximo dato a conseguir para avanzar en esa línea.
