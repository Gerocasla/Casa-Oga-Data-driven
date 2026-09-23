# Problemas de calidad de datos — Casa Óga

> **Corte:** agosto 2026 · **Fuente de los números:** `Datasets_Normalizados/` (15 fuentes)
> **Verificado con:** `EDA/calidad_2026.py` · **Actualizado:** 22-09-2026
>
> Este archivo es el insumo de la **Sección 1 del Entregable 2 · Parte B** (Hallazgos y Plan de Mejora de Calidad).
> Cada vez que se resuelva un hallazgo, marcarlo acá y anotarlo en `REGISTRO-CAMBIOS-DATASETS.md`.

---

## Resumen

| | |
|---|---|
| Hallazgos abiertos | **12** |
| Hallazgos resueltos por la normalización | **2** |
| Fuentes sin ningún problema | Proveedores, Tiendas*, Calendario*, Stock_Deposito_Central, Devoluciones_SKU, Ordenes_Compra |

\* Tiendas tiene un problema de consistencia cruzada con Ventas (H2), no interno. Calendario no cubre 2026 (H12).

**Dato clave:** los problemas de unicidad, exactitud y validez están **confinados al tramo 2022-2025**. El tramo 2026 (60.064 filas nuevas) no presenta duplicados, negativos ni nulos en Ventas ni en Stock.

El período 2026 llegó en una **segunda entrega de datasets**: son los mismos archivos, con los meses de 2026 agregados. Se verificó que el tramo 2022-2025 quedó idéntico al de la primera entrega (mismas filas, mismos totales: $32.538,4 M y 750.538 unidades). Por lo tanto, el diagnóstico de calidad del tramo histórico sigue vigente sin cambios, y los hallazgos nuevos se limitan a lo que aporta el tramo 2026.

---

## Tabla maestra

| ID | Problema | Fuente(s) | Dimensión | Magnitud | Dónde ocurre | Estado |
|---|---|---|---|---|---|---|
| H1 | Claves duplicadas | Ventas, Stock | Unicidad | 2.378 en cada una | Solo 2022-25 | Abierto |
| H2 | SKUs duplicados en el maestro | Productos_catalogo | Unicidad | 15 ids | — | Abierto |
| H3 | Ventas anteriores a la apertura | Ventas, Tiendas | Consistencia | 11.058 filas · $1.471,7 M | 6 tiendas | Abierto |
| H4 | Valores negativos imposibles | Ventas, Stock | Exactitud, Validez | 2.317 + 1.209 | Solo 2022-25 | Abierto |
| H5 | Venta sin stock / mayor al stock | Ventas × Stock | Consistencia | 1.020 y 5.727 | Ambos tramos | Abierto |
| H6 | Stock en tránsito sin conciliar | Stock, Transferencias | Consistencia | 8.771 vs 936 (9×) | Ambos tramos | Abierto |
| H7 | Liquidaciones incoherentes | Liquidaciones, Catálogo | Consistencia | 90 de 108 | — | Abierto |
| H8 | Precio de venta vs historial | Ventas, Historial_Precios | Consistencia | 33% de las filas | Ambos tramos | Abierto |
| H9 | Descuentos fuera de rango | Liquidaciones, Promociones | Validez | 3 + 2 | — | Abierto |
| H10 | Promociones duplicadas e inválidas | Promociones_Comerciales | Unicidad, Validez | 2 ids + 2 fechas | — | Abierto |
| H11 | Faltantes de costo | Catálogo, Historial_Precios | Completitud | 22 SKUs · 40 vigencias | — | Abierto |
| H12 | Fuentes sin cobertura de 2026 | Devoluciones, Calendario, Catálogo | Actualidad | 3 fuentes | 2026 | Abierto |
| ~~R1~~ | ~~Variantes de categoría~~ | ~~Catálogo, Promociones~~ | ~~Consistencia~~ | ~~11 valores para 7~~ | — | **Resuelto** |
| ~~R2~~ | ~~Formato mixto de fecha~~ | ~~Liquidaciones~~ | ~~Validez~~ | ~~8 registros~~ | — | **Resuelto** |

---

## Detalle

### H1 · Claves duplicadas en Ventas y Stock
2.378 combinaciones (mes, tienda, SKU) repetidas en cada archivo, más 56 filas exactas en Ventas y 21 en Stock.
En Ventas, 2.322 duplicados tienen valores distintos entre sí y 811 tienen un registro en cero.
**Se originan en H2:** todas corresponden a los 15 SKUs cargados dos veces en el catálogo.
**No ocurre en 2026** (0 duplicados en las 60.064 filas nuevas).

### H2 · SKUs duplicados en el maestro de producto
15 identificadores aparecen en dos filas, **idénticas en todo salvo el proveedor**. Es la causa raíz de H1.
Puede ser legítimo (producto comprado a más de un proveedor) o un error de carga al cambiar de proveedor sin dar de baja el registro anterior. El negocio no lo confirmó.

### H3 · Ventas registradas antes de la apertura de la tienda
11.058 filas por **$1.471,7 M** en seis tiendas, con ventas anteriores a su `fecha_apertura`:

| Tienda | Abre | Meses de venta previos | Venta previa |
|---|---|---:|---:|
| T25 | feb-2025 | 36 | $773,4 M |
| T07 | may-2024 | 27 | $385,1 M |
| T19 | jun-2023 | 17 | $148,5 M |
| T21 | jun-2023 | 17 | $137,7 M |
| T05 | sep-2022 | 8 | $25,1 M |
| T22 | abr-2022 | 2 | $1,9 M |

O la fecha de apertura está mal, o las ventas están mal asignadas. **Afecta cualquier análisis por antigüedad de tienda.**

### H4 · Valores negativos imposibles
- **Ventas:** 2.317 filas con unidades y monto negativos a la vez (mínimo −26 unidades / −$1.705.312).
- **Stock:** 1.209 filas con stock disponible negativo (mínimo −152 unidades).

Las 2.317 filas de venta negativa **coinciden una a una con los registros de Devoluciones_SKU** (misma clave, mismas unidades), así que el dato es recuperable.
Los motivos contradicen lo declarado por el negocio: solo el 20% son devoluciones de cliente; el resto es daño en logística, producto sin rotación, error de picking y defecto de fabricación.
**No ocurre en 2026.**

### H5 · Venta sin stock o mayor al stock
- 1.020 filas con venta mayor a cero y stock en cero el mismo mes (833 en 2022-25, **187 en 2026**).
- 5.727 filas con venta superior al stock disponible (5.278 + **449 en 2026**).

Es el único problema de consistencia que **persiste en 2026**. Apunta a una falta de sincronización entre el punto de venta y el sistema de inventario, o a que el stock se informa a fin de mes y la venta es del mes completo.

### H6 · Stock en tránsito sin conciliar con transferencias
A ago-2026 el campo `stock_en_transito` registra **8.771 unidades**, mientras que las transferencias en curso a esa fecha explican **936** (28 envíos). Relación de **9×**.
A dic-2025 la relación era de 20×, así que la brecha se achicó pero sigue sin cerrar.
Las series están correlacionadas (0,89), lo que sugiere que el campo mide algo más amplio — probablemente incluya órdenes de compra pendientes de recepción. **No hay definición documentada del campo.**

### H7 · Liquidaciones incoherentes con el catálogo
- **90 de las 108** liquidaciones con motivo «Discontinuación» corresponden a SKUs que figuran como **Activos**.
- 12 liquidaciones tienen `tienda = "Todas"`, que no es un identificador válido de tienda.
- 278 de 496 liquidaciones con tienda asignada recaían sobre posiciones sin stock ese mes (medido al corte anterior).

### H8 · Precio de venta inconsistente con el historial de precios
El precio implícito (venta ÷ unidades) comparado con el **precio de lista actual** del catálogo: mediana 0,92, rango 0,14 a 1,21. Hay 2.731 filas (1,1%) que superan el precio de lista.
Comparado con el precio **vigente según Historial_Precios** en ese mes, lo supera en más de 1,5 veces en el **33%** de las filas (máximo 5,4×).
Las ventas parecen valuadas con el precio actual y no con el histórico. **Invalida cualquier análisis de elasticidad o de impacto de descuentos.**

### H9 · Descuentos fuera de rango
- **Liquidaciones:** 3 valores fuera de [0, 100] → 120%, −10%, 120%.
- **Promociones:** 2 valores → 150%, −15%.
- **Presupuesto:** 3 valores negativos y 309 ceros concentrados en los primeros meses de 2022.

### H10 · Promociones duplicadas e inválidas
- 1 fila exactamente duplicada y 2 identificadores repetidos (uno de ellos, `PROMO0101`, con dos descuentos distintos: 15% y 5%).
- 2 promociones con fecha de fin anterior a la de inicio.

### H11 · Faltantes de costo
- **22 SKUs** sin `costo_unitario` en el catálogo.
- **40 vigencias** (de 22 SKUs) sin costo en el historial de precios.
- No se puede completar desde ninguna otra fuente. Impide calcular margen y capital inmovilizado para esos productos.
- Menores: 65 de 119 promociones sin `medio_pago` y 54 sin `evento_asociado`.

### H12 · Fuentes sin cobertura de 2026
Ventas y Stock llegan a ago-2026, pero tres fuentes se cortan antes:

| Fuente | Último dato | Consecuencia |
|---|---|---|
| Devoluciones_SKU | 28-dic-2025 | No se puede calcular tasa de devolución en 2026 |
| Calendario | 31-dic-2025 | Sin temporada ni feriados para 8 meses de venta |
| Productos_catalogo | alta 29-jun-2025 | Ningún SKU dado de alta; el maestro quedó congelado |

---

## Resueltos por la normalización (22-09-2026)

Aplicados por `EDA/normalizar_datasets.py` sobre `Datasets/` → `Datasets_Normalizados/`. Total: 2.712 celdas.

### R1 · Variantes de escritura de categoría — **resuelto**
El catálogo tenía 11 valores para 7 categorías reales (`Decoración`/`DECO`/`Decoracion`, `Textil Hogar`/`TEXTIL_HOGAR`/`Textil hogar`) y Promociones tenía 10.
Ambas fuentes quedan en los mismos 7 valores canónicos: `Bano, Cocina y mesa, Decoracion, Iluminacion, Muebles, Organizacion, Textil hogar`.

### R2 · Formato mixto de fecha en Liquidaciones — **resuelto**
8 registros tenían `fecha_fin` como `AAAA-MM-DD 00:00:00` en lugar de `AAAA-MM-DD`. Eran válidos, no ilegibles: el TP1 los había descartado como "no parseables". Quedan los 593 registros con formato uniforme.

---

## Pendiente de confirmar con el negocio

Las siguientes preguntas condicionan cómo se corrige cada hallazgo y están en `Preguntas-Calidad-de-Datos-Ronda-2.docx`:

1. **H2** — ¿Los 15 SKUs duplicados son multi-proveedor legítimo o error de carga? ¿Cuál es el registro válido?
2. **H3** — ¿Está mal la fecha de apertura o la asignación de las ventas?
3. **H4** — ¿Se reemplazan las ventas negativas por el dataset de devoluciones? ¿Por qué solo el 20% son de cliente?
4. **H6** — ¿Qué incluye exactamente `stock_en_transito`?
5. **H8** — ¿Con qué precio se valúan las ventas: el vigente del mes o el actual?
6. **H12** — ¿Van a enviar Devoluciones, Calendario y Catálogo actualizados a 2026?
