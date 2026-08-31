# Casa Óga — CSVs limpios (metodología)

Este paquete contiene los 6 CSV originales del proyecto, con las correcciones de calidad de datos descriptas abajo. Los archivos que no tenían problemas (`Tiendas.csv`, `Calendario.csv`) se incluyen sin cambios. Los que sí se corrigieron llevan el sufijo `_limpio` y **agregan columnas de auditoría** (originales/flags) para que quede trazable qué se tocó — no se borra información silenciosamente.

Corte de los datos: enero 2022 – diciembre 2025 (48 meses), 28 tiendas.

> **⚠️ Corrección importante (31-ago-2026) — deduplicación por clave.** La versión original de esta metodología eliminaba solo las filas **100% idénticas** de Stock y Ventas (21 y 56 filas respectivamente). Al reconstruir el cálculo de dead stock se descubrió que eso dejaba pasar **~2.378 filas por archivo** que comparten la misma clave `(fecha_mes, id_tienda, id_producto)` pero tienen **valores distintos** — es decir, dos registros contradictorios para el mismo producto, en la misma tienda, en el mismo mes. `drop_duplicates()` sin especificar columnas no las detecta. Se concentran en los mismos 15 SKUs que ya estaban duplicados en el catálogo. **Ahora se deduplica por clave** (conservando la primera ocurrencia), igual que ya se hacía en el catálogo. El detalle está en la sección de Stock y Ventas.

---

## Productos_catalogo_limpio.csv (815 → 800 filas)

**1. Categorías normalizadas (21 filas).** El campo `categoria` tenía variantes de mayúsculas/acentos/guiones para las mismas categorías: `"Decoración"` (8), `"Textil Hogar"` (6), `"DECO"` (5), `"TEXTIL_HOGAR"` (2). Se normalizaron a la forma estándar (`Decoracion`, `Textil hogar`, etc.). El valor original queda en la columna `categoria_original`.

**2. SKUs duplicados eliminados (15 filas).** 15 `id_producto` aparecían en 2 filas del catálogo (mismo SKU, mismo precio/costo). Se conservó la primera ocurrencia. IDs afectados: SKU00016, SKU00058, SKU00112, SKU00311, SKU00330, SKU00333, SKU00370, SKU00430, SKU00433, SKU00453, SKU00533, SKU00552, SKU00566, SKU00737, SKU00785.

**3. Costo unitario faltante, imputado (22 filas).** 22 SKUs no tenían `costo_unitario` cargado. Se imputó con la **mediana de costo de su categoría** (después de la limpieza anterior). Se agregó la columna `costo_unitario_imputado` (`True`/`False`) para poder filtrar o recalcular con otro criterio — es una estimación, no el dato real.

**Nota sobre columnas nativas del catálogo (no se tocan, pero se usan en dead stock):** el catálogo trae de origen `subcategoria`, `proveedor`, `fecha_alta_catalogo`, `fecha_baja_catalogo` y `estado` (Activo/Discontinuado). No requieren limpieza, pero son la base para calcular la antigüedad real de cada SKU y para identificar productos discontinuados con stock remanente.

**Ojo con `fecha_baja_catalogo`:** al reconstruir el cálculo de dead stock apareció un error de comparación de fechas. `fecha_mes` representa el mes completo (`2025-12-01` = todo diciembre), pero las bajas de catálogo caen en cualquier día del mes (por ejemplo `2025-12-23`). Comparar la baja contra el día 1 del mes de corte hacía que **ninguna** baja de ese mes contara como discontinuada. Hay que comparar contra el **fin de mes**. Vale para cualquier análisis que cruce estas fechas con la grilla mensual.

---

## Stock_SKU_tienda_mensual_limpio.csv (239.336 → 236.958 filas)

**1. Deduplicación por clave (2.378 filas).** Se elimina toda fila que repita la clave `(fecha_mes, id_tienda, id_producto)`, conservando la primera ocurrencia. De esas, solo 21 eran duplicados 100% idénticos; **las otras 2.357 tenían valores distintos para la misma clave** y no las detectaba la limpieza original. Concentradas en los 15 SKUs duplicados del catálogo.

*Recomendación:* conservar la primera ocurrencia es una convención, no una verdad. Si el equipo de Sistemas puede decir cuál de los dos registros es el bueno (¿el último cargado? ¿el de mayor stock?), conviene cambiar el criterio. Mientras tanto queda documentado como decisión.

**2. Stock disponible negativo corregido a 0 (1.209 filas).** `stock_disponible` no puede ser negativo. Se llevó a 0 y se marcó con `stock_disponible_flag_corregido`. **No sabemos la causa raíz** (¿ajuste de inventario mal registrado? ¿bug de integración?) — vale la pena preguntarle al equipo de Inventario antes de confiar en este supuesto para un modelo productivo.

---

## Ventas_SKU_tienda_mensual_limpio.csv (239.336 → 236.958 filas)

**1. Deduplicación por clave (2.378 filas).** Mismo criterio que en Stock. De esas, 56 eran duplicados exactos y **2.322 tenían valores distintos para la misma clave**.

**2. Unidades/venta negativas corregidas a 0 (2.317 filas).** `unidades_vendidas` y `venta_neta` eran negativas juntas en las mismas filas (nunca una sin la otra). Se llevaron ambas a 0 y se marcaron con `venta_flag_corregido`. **Ojo:** esto podría estar escondiendo devoluciones reales mal codificadas. Si el negocio maneja devoluciones como ventas en negativo, esta limpieza las está descartando en vez de tratarlas como una categoría propia. Confirmar con Sistemas/Ventas antes de dar esto por cerrado.

**Particularidad del dataset a tener presente.** Después de limpiar, **toda combinación SKU–tienda con stock registró al menos 1 unidad vendida en los últimos 12 meses**. No existe el caso "nunca vende". Esto limita el poder de cualquier regla basada en ausencia de ventas y conviene tenerlo en cuenta al extrapolar a datos reales — probablemente sea un artefacto de cómo se generó el dataset del curso.

---

## Liquidaciones_limpio.csv (508 → 508 filas, ninguna eliminada)

**1. Fechas no parseables, marcadas (8 filas).** `fecha_inicio`/`fecha_fin` con formato inválido se dejaron **en blanco** en vez de inventar una fecha, y se marcaron con `fecha_flag_invalida`. Los valores originales (como texto) se conservan en `fecha_inicio_original` / `fecha_fin_original`.

**2. Descuento fuera de rango, acotado (3 filas).** `descuento_pct` con valores negativos o mayores a 100% se acotaron al rango [0, 100] y se marcaron con `descuento_flag_corregido`.

**Nota de alcance:** las liquidaciones cubren 1.560 unidades vendidas en 4 años (0,2% de las unidades totales). Es un volumen chico — cualquier porcentaje calculado sobre esta tabla (caídas de margen, por ejemplo) es estadísticamente frágil y no conviene extrapolarlo al negocio completo.

---

## Tiendas.csv y Calendario.csv

Sin problemas de calidad detectados — se incluyen tal cual el original.

---

## Resumen de columnas de auditoría agregadas

| Archivo | Columna agregada | Qué indica |
|---|---|---|
| Productos_catalogo_limpio | `categoria_original` | Valor de categoría antes de normalizar |
| Productos_catalogo_limpio | `costo_unitario_imputado` | `True` = el costo fue estimado (mediana de categoría), no es el dato real |
| Stock_SKU_tienda_mensual_limpio | `stock_disponible_flag_corregido` | `True` = el valor original era negativo y se llevó a 0 |
| Ventas_SKU_tienda_mensual_limpio | `venta_flag_corregido` | `True` = unidades/venta originales eran negativas y se llevaron a 0 |
| Liquidaciones_limpio | `fecha_flag_invalida` | `True` = fecha_inicio y/o fecha_fin no se pudo interpretar |
| Liquidaciones_limpio | `fecha_inicio_original` / `fecha_fin_original` | Texto original de la fecha, tal como venía en el archivo |
| Liquidaciones_limpio | `descuento_flag_corregido` | `True` = descuento_pct estaba fuera de 0–100% y se acotó |

Si para el modelo prefieren excluir en vez de corregir las filas marcadas, es tan simple como filtrar por esas columnas de flag antes de entrenar.

---

## Implementación de referencia

La limpieza descripta acá está implementada en la función `load_clean_data()` de `calculo_dead_stock.py`, que es la que usan todos los análisis del proyecto. Cualquier cambio de criterio debería hacerse ahí para que se propague de forma consistente y no queden números calculados con reglas distintas — que es exactamente el problema que originó la corrección del 31-ago-2026.

---

## Dato pendiente de origen

El relevamiento oficial a la empresa (Grupo 1) menciona un `Proveedores.csv` (lead time, lote mínimo de pedido, condiciones de devolución por proveedor) como "ya entregado", pero ese archivo **no está** entre los CSV recibidos ni en el proyecto. Es el dato más directo para poder estimar una cadencia real de reposición — está pendiente de reclamar.

---

Metodología completa y KPIs de negocio derivados de estos datos: ver el mini-análisis de KPIs y el reporte [Casa Óga en Números](https://claude.ai/code/artifact/e5c495a6-c672-47fe-9d54-795db8806a7e). Evolución histórica del % de stock vendido: [Histórico % vendido](https://claude.ai/code/artifact/851f10a1-61a4-4156-befb-158561905139). Diagnóstico de dead stock, semáforo propuesto y explorador por tienda: [Panel de Dead Stock](https://claude.ai/code/artifact/d360de71-73a6-43a5-80c5-d099da6233b6).
