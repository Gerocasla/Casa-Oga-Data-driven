# EDA y calidad de datos — Resultados recopilados (insumo Entregable 2)

> **Estado:** recopilación. No se modificó el entregable. Todo lo de acá sale de correr `eda.py` y `eda_chequeos_2.py` sobre los 15 CSV de `Data-Driven\Datasets` (sin modificarlos).
> Logs completos: `resultados\eda_log.txt` y `resultados\eda_chequeos_2_log.txt` · Gráficos: `graficos\` · Tablas: `resultados\*.csv`
> "Limpio" = mismo criterio V1 del TP1 (dedup por clave conservando 1ra ocurrencia, negativos a 0, categorías normalizadas, catálogo dedup).

---

## 1. Perfil general de las 15 fuentes

| Fuente | Filas | Período | Granularidad | Nulos | Duplicados |
|---|---|---|---|---|---|
| Ventas_SKU_tienda_mensual | 239.336 (236.958 limpias) | ene-22 → dic-25 (48 meses) | mes · tienda · SKU | 0 | 56 exactos · 2.378 por clave |
| Stock_SKU_tienda_mensual | 239.336 (236.958 limpias) | ene-22 → dic-25 | mes · tienda · SKU | 0 | 21 exactos · 2.378 por clave |
| Productos_catalogo | 815 (800 SKUs) | altas ene-22 → jun-25 | SKU | costo 22 · baja 647 (esperable) | 15 SKUs |
| Tiendas | 28 | aperturas ago-14 → feb-25 | tienda | 0 | 0 |
| Calendario | 1.461 | 01-ene-22 → 31-dic-25 | día | evento 1.373 (esperable) | 0 |
| Liquidaciones | 508 | inicio mar-22 → dic-25 | liquidación (SKU·tienda) | 0 | 0 |
| Devoluciones_SKU | 2.317 (9.583 uds) | mar-22 → dic-25 | devolución (SKU·tienda·día) | 0 | 0 |
| Historial_Precios_SKU | 1.498 (800 SKUs) | vigencias ene-22 → **jul-26** | SKU · vigencia | costo 40 (22 SKUs) · hasta 800 (vigente) | 0 |
| Ordenes_Compra | 3.000 | pedidos feb-22 → **jul-26** | OC (SKU·proveedor) | 0 | 0 |
| Presupuesto_Ventas_Tienda_Categoria | 10.976 | ene-22 → **ago-26** (56 meses) | mes · tienda · categoría | 0 | 0 |
| Promociones_Comerciales | 119 | ene-22 → **ago-26** | promoción (categoría·canal) | medio_pago 65 · evento 54 | 1 exacto · 2 ids repetidos |
| Proveedores | 10 | — | proveedor | 0 | 0 |
| Stock_Deposito_Central | 23.858 (798 SKUs) | ene-22 → **ago-26** | mes · SKU | 0 | 0 |
| Transferencias_Stock | 4.200 | envíos feb-22 → **sep-26** | transferencia | 0 | 0 |
| Costo_almacenamiento | 7 | — | categoría | 0 | 0 |

**Integridad referencial:** todos los SKUs de las 8 tablas transaccionales existen en el catálogo; todas las tiendas existen en Tiendas (excepto `Todas` en Liquidaciones ×12 y `DEP-CENTRAL` en Transferencias, valores válidos); todos los proveedores existen en Proveedores. 2 SKUs del catálogo nunca tienen fila de ventas.

---

## 2. Analítica descriptiva (datos limpios)

### 2.1 Volumen y evolución
- Venta total 2022-2025: **$32.538,4 M** · **750.538 unidades** · precio medio por unidad **$43.353** (crudo sin limpiar: $32.352,9 M / 746.414 uds).
- Por año: 2022 $1.812 M · 2023 $6.323 M (+249%) · 2024 $10.669 M (+69%) · 2025 $13.734 M (+29%).
- Posiciones SKU-tienda por mes: **17 en ene-22 → 8.073 en dic-25**. SKUs con venta: 204 (2022) → 730 (2025). Todas las tiendas tienen ventas desde ene/feb-22.
- Unidades por posición por mes: **plana, ~3,2** todo el período → el crecimiento es 100% por más posiciones (catálogo × tiendas), no por más venta por producto.
- 2025: unidades mensuales planas (25.096 ene → 27.519 jul → 25.781 dic). Crecimiento interanual se desacelera de +47% (ene-25) a +6,6% (dic-25).

### 2.2 Estadísticas por fila (2025, SKU-tienda-mes)
- Unidades: media 3,21 · mediana 2 · p75 4 · p95 11 · p99 17 · máx 31.
- Venta neta: media $140.114 · mediana $65.048 · p95 $551.997 · máx $1,94 M.
- Stock dic-25 por posición: media 16,8 · mediana 10 · p95 54 · máx 134. Posiciones con stock > 0: **7.993**; SKUs con stock: 647 (634 activos + 13 discontinuados).
- 18,96% de filas de venta con 0 unidades. Outliers IQR (crudo): 20.785 filas en unidades, 17.450 en stock (distribución asimétrica, no errores).

### 2.3 Distribución por dimensiones
- **Categoría** (% venta / % SKUs / margen lista): Decoración 22,8 / 19,6 / 45,3 · Cocina y mesa 19,1 / 15,2 / 45,9 · Iluminación 14,2 / 10,8 / 46,0 · Textil hogar 12,7 / 15,9 / 44,4 · Muebles 11,8 / 14,6 / 44,1 · Organización 11,1 / 11,8 / 43,8 · Baño 8,4 / 12,1 / 44,7. Margen teórico de lista promedio 44,9%.
- **Región:** AMBA 39,3% (11 tiendas) · Centro 21,9% (6) · NOA 17,9% (5) · Cuyo 17,2% (5) · Patagonia 3,7% (1).
- **Tienda:** muy pareja, de 3,0% a 4,1% cada una (máx T24 $1.342 M, mín T14 $981 M). Correlación venta vs m² = **−0,24**. Formato: Mediano 43,3% · Grande 39,4% · Chico 17,3%.
- **Pareto SKU:** 248 de 798 SKUs con venta (31,1%) = 80% de la venta; top 10% = 48,7%. En 2025: 246 de 730.

### 2.4 Relaciones entre variables
- Correlación fila a fila unidades vs stock: **0,77**.
- 2025/2023: venta $ ×2,17 · unidades ×2,13 · stock total promedio mensual ×2,14 · stock por posición ×1,03.
- **Cobertura (meses de stock)** según cómo se mida:

| Definición | ene-23 | dic-25 | prom. 2023 | prom. 2025 |
|---|---|---|---|---|
| stock / unidades del mes | 5,29 | 5,26 | 5,27 | 5,30 |
| stock / promedio 3 meses | 5,79 | 5,21 | 5,61 | 5,33 |
| stock / promedio 12 meses (la del TP1) | **10,55** | **5,16** | **8,09** | **5,77** |
| mediana por posición | 5,11 | 5,23 | — | — |

- **Presupuesto vs real 2022-2025:** cumplimiento 90,6% · 91,0% · 91,5% · 91,7%. Por categoría 90,6-92,1%, por tienda 90,1-92,2%, por celda mediana 91,2%.
- **Devoluciones:** tasa de devolución estable ~1,3% de las unidades vendidas por año. Motivos (unidades): dañado en logística 2.067 · sin rotación/no vendido 2.013 · devolución de cliente (cambio) 1.930 · error de picking 1.787 · defecto de fabricación 1.786.
- **Lead time real de OC vs declarado en Proveedores:** coincide (real = declarado +1 día en todos, rango ±4). Ninguna OC por debajo del pedido mínimo. Costo OC / costo catálogo: mediana 1,00 (0,85-1,16).
- **Transferencias:** 2.258 desde depósito · 1.460 entre tiendas · 482 hacia depósito. Tránsito 3-21 días (mediana 12).

---

## 3. Calidad de datos — hallazgos por fuente

| Fuente | Hallazgos |
|---|---|
| Ventas | 2.378 claves duplicadas (2.322 con valores distintos, 811 con un registro en 0), todas en los 15 SKUs duplicados del catálogo, en los 4 años (528/1.060/1.332/1.836). 2.317 filas negativas (unidades y venta juntas). **10.903 filas / $1.475,9 M de venta antes de la fecha de apertura de 6 tiendas** (ver D3). |
| Stock | 2.378 claves duplicadas (2.357 con valores distintos). 1.209 negativos (mín −152). 1.790 filas con venta > 0 y stock = 0 en el mismo mes; 4.282 con venta > stock. **stock_en_transito no se explica por Transferencias** (ver D6). |
| Catálogo | 15 SKUs duplicados que difieren **solo en proveedor**. 11 valores de categoría para 7 reales (21 filas). 22 SKUs sin costo (tampoco tienen costo en Historial ni en otra fuente directa). Sin precio < costo, sin fechas incoherentes, estado consistente con fecha de baja. |
| Liquidaciones | 3 descuentos fuera de rango (120, −10, 120). 12 con tienda `Todas`. **8 fechas de fin con formato `AAAA-MM-DD 00:00:00`** — son válidas, no ilegibles (ver D5). **79 de 93 liquidaciones "Discontinuación" son de SKUs Activos**. **278 de 496 liquidaciones (con tienda) caen en SKU-tienda sin stock ese mes**. |
| Devoluciones | Sin problemas internos. **Coinciden 1 a 1 con las 2.317 filas de venta negativa** (misma clave y mismas unidades) (ver D4). |
| Historial_Precios | Vigencias sin solapes ni huecos; última vigencia = catálogo (800/800); 1ra vigencia = fecha de alta (800/800). 22 SKUs sin costo. 176 vigencias que empiezan en 2026. **Inconsistente con Ventas** (ver D7). Saltos de precio entre vigencias: mediana +86%, p95 +326%. |
| Ordenes_Compra | Sin nulos ni fechas invertidas; lead time coherente con Proveedores. **532 pedidos con fecha 2026** (ver D8). |
| Presupuesto | 3 valores negativos (T22 jun-22, T17 jul-22 −$963 mil y −9 uds, T24 ene-23). 309 ceros concentrados ene-may 2022. 252 celdas sin venta real. Cumplimiento sospechosamente uniforme (~91% en todo nivel). 1.568 celdas de 2026. |
| Promociones | 2 ids repetidos (PROMO0083 exacto; PROMO0101 con 15% y 5%). 2 con fecha fin < inicio (Navidad 31-dic → 15-dic). Descuentos 150% y −15%. 3 variantes de categoría. 11 promos de 2026. |
| Proveedores | Sin problemas. |
| Stock_Deposito_Central | Sin negativos ni duplicados. 5.072 filas de 2026. |
| Transferencias | Sin fechas invertidas ni origen = destino. 826 envíos en 2026. 1.803 de 4.200 con SKU-tienda destino sin fila de stock ese mes. |
| Costo_almacenamiento | Precio promedio coincide con catálogo. **Criterio 1,5% del precio de lista mensual** (ver D9). |
| Tiendas / Calendario | Sin problemas internos. Tiendas: fechas de apertura incoherentes con ventas (D3). |

---

## 4. ⚠️ Discrepancias detectadas (datos que no concuerdan)

**D1 — La estacionalidad del TP1 es un efecto del crecimiento, no estacionalidad real.**
El índice 143 (dic) vs 61 (ene) del TP1 se reproduce exacto, pero se calcula normalizando cada mes contra el promedio de su año, en un negocio que pasó de 17 a 8.073 posiciones. Ajustando por tendencia (media móvil 12m) el índice queda entre **101 y 105 todos los meses**; en 2025 (año sin crecimiento) va de 96 a 104; unidades por posición planas en 3,2. Por categoría, sobre tendencia, ningún mes pasa de 112. Tampoco se ve efecto Hot Sale/Black Friday/Navidad a nivel mensual. → Afecta TP1: 1.2 Situación de mercado, 5.4.1 (justificación del corte de 12 meses por "temporada alta"), 5.4.3 (Organización 79 vs 117).

**D2 — "La cobertura mejoró de 10,6 a 5,2 meses" también es efecto del crecimiento.**
Se reproduce solo con stock / promedio de 12 meses: en ene-23 ese promedio incluye los meses de arranque de 2022, cuando casi no había ventas. Con cualquier otra medida la cobertura está **plana (~5,2-5,3)**. → Afecta TP1: Resumen ejecutivo, 1.2, 5.3 y la corrección #2 del feedback (el argumento "mejoró" tampoco se sostiene: lo correcto sería "estable").

**D3 — Ventas antes de la apertura de las tiendas.**
6 tiendas venden desde ene/feb-22 aunque abrieron después: T25 Córdoba (abre feb-25, 36 meses antes, $776 M) · T07 Córdoba (may-24, 27 meses, $391 M) · T19 y T21 Mendoza (jun-23, 17 meses) · T05 Bs As (sep-22, 8 meses) · T22 CABA (abr-22, 2 meses). O la fecha de apertura está mal, o las ventas están mal asignadas.

**D4 — Las ventas negativas SON exactamente las devoluciones, pero los motivos contradicen al negocio.**
Las 2.317 devoluciones coinciden 1 a 1 con las 2.317 filas negativas. El TP1 dice (según el negocio) que son "mayormente devoluciones de clientes", pero solo 466 (20%) son "Devolución de cliente (cambio)"; el resto es dañado en logística, sin rotación/no vendido, error de picking y defecto. Además el TP1 las lleva a 0: se pierden 9.583 unidades (el criterio del TP1 decía que se esperaba este dataset para tratarlas aparte — ya llegó).

**D5 — Las 8 "fechas no parseables" de Liquidaciones sí son válidas.**
Son `fecha_fin` con formato `2023-12-24 00:00:00`. El TP1/metodología las deja en blanco; se pueden recuperar sin inventar nada.

**D6 — stock_en_transito no concuerda con Transferencias.**
Dic-25: 23.528 unidades en tránsito en Stock vs 868 que surgen de Transferencias en curso a fin de mes (promedio 14.217 vs 648). Van correlacionadas (0,89) pero con escala ~20x distinta. Puede que el tránsito incluya OC de proveedores u otra definición.

**D7 — Historial_Precios no concuerda con Ventas.**
El precio implícito (venta/unidades) está entre 85% y 100% del precio de lista **actual del catálogo** en el 100% de las filas, pero comparado con el precio **vigente según Historial** en ese mes es >1,5 veces en el 39% de los casos (hasta 4,9x). Es decir: las ventas parecen calculadas con el precio de hoy, no con el histórico.

**D8 — Fuentes con datos posteriores al corte (2026).**
Ventas/Stock/Liquidaciones/Devoluciones/Calendario terminan en dic-25; pero Stock depósito y Presupuesto llegan a ago-26, OC a jul-26 (recepción sep-26), Transferencias a sep-26, Historial a jul-26, Promociones a ago-26.

**D9 — Costo de almacenamiento: 1,5% (dataset) vs 2% (TP1).**
El TP1 usa 5% mensual = 2% almacenamiento + 3% oportunidad "confirmado por el negocio". El dataset `Costo_almacenamiento` dice 1,5% del precio de lista por unidad y mes.

**D10 — Duplicados: cifras del TP1 5.1 no se reproducen.**
TP1 5.1: "2.378 combinaciones, 2.135 con valores distintos y 803 con un registro en cero". Recalculado: Ventas **2.322** distintos / **811** con cero; Stock **2.357** distintos (la metodología .md dice 2.322 y 2.357, coincide con esto; el Word no).

**D11 — Liquidaciones por "Discontinuación" sobre SKUs activos y sin stock.**
79 de 93 son de SKUs que siguen Activos en el catálogo; y 278 de 496 liquidaciones caen en SKU-tienda sin stock ese mes.

**D12 — "Ticket medio $43.353" (TP1 1.1) no es ticket.**
Es venta / unidades = precio medio por unidad. No hay datos de transacciones para calcular ticket.

**D13 — TP1 dice que faltan datasets que ya están.**
TP1 (Resumen, 2.6, 5.1, 5.6) da como no recibidos: transferencias, promociones, presupuesto, devoluciones, Proveedores y costos por categoría. Hoy están los 6 en `Datasets`.

**Cifras del TP1 que SÍ se reproducen:** $32.538 M, 750.538 uds, venta 2025 $13.734 M, AMBA 39,3%, 800 SKUs / 7 cat / 25 subcat, 634 activos con stock, 7.993 posiciones con stock dic-25, 2.776 en ene-23, mix por categoría, margen 44,9%, Pareto 248/798, liquidaciones 33→247, 1.209 stock negativo (mín −152), 2.317 ventas negativas, 22 sin costo, 3 descuentos fuera de rango, 12 "Todas", 19% filas en cero, ventas ×2,13 y stock ×2,14.
*(No se recalculó el dead stock / semáforo: 661, $83,9 M, 345/652 — requiere el script original `calculo_dead_stock.py`, que no está en las carpetas.)*

---

## 5. Preguntas abiertas para el equipo (no escribir nada sobre esto sin respuesta)
Ver `Data-Driven\Recordatorios\04-tp2-eda-pendientes.md`.
