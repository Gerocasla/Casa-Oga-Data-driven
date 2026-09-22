# Entregable 2 — Estado y pendientes

> **22-09-2026 — ATENCION, cambio de base de datos.** Llegaron versiones nuevas de Ventas, Stock y Liquidaciones desde el repo: ahora cubren hasta **ago-2026** (antes dic-2025). Ventas y Stock pasan de 239.336 a 299.400 filas; Liquidaciones de 508 a 593. **Todos los numeros del EDA y del TP1 estan calculados sobre el corte viejo y hay que recalcularlos.** Detalle en `REGISTRO-CAMBIOS-DATASETS.md`.
>
> **Datos a usar de ahora en mas:** `Datasets_Normalizados/` (representacion unificada, sin tildes ni enie, fechas AAAA-MM-DD). `Datasets/` queda como copia intacta de la catedra. Toda modificacion se anota en `REGISTRO-CAMBIOS-DATASETS.md`.
>
> **Un companiero subio `Entregable 2 - Parte A - COMPLETADO.docx`** al repo (copiado a `Entregable/Entregable 2/`). Revisar que no se pise con lo que armemos nosotros.

- **Consigna/plantilla:** `Entregable\Entregable 2\Entregable 2 - Parte A - Alcance y Evaluacion de Calidad de Datos.docx` (NO modificada todavía)
- **EDA corrido (15 fuentes):** `Entregable\Entregable 2\EDA\` → `HALLAZGOS_EDA.md` (resumen completo), `eda.py`, `eda_chequeos_2.py`, `resultados\`, `graficos\`
- **Preguntas al negocio (ronda 2):** `Entregable\Entregable 2\Preguntas-Calidad-de-Datos-Ronda-2.docx` (22 preguntas: costo de 22 SKUs, historial de precios, stock negativo, devoluciones, descuentos fuera de rango, presupuesto). Generado con `gen_preguntas.py`.
- **Estado:** ⏳ Recopilación terminada. Esperando respuestas del usuario y del negocio antes de escribir el entregable.

## Qué pide la plantilla
1. Carátula: integrantes, legajos, rol en esta fase, fecha.
2. Sección 2.3: tabla Métrica / Resultado / Insight (EDA: perfil, estadísticas, evolución, distribución, relaciones) + anexo con gráficos.
3. Sección 3.1: matriz fuente × 7 dimensiones (Completitud, Consistencia, Exactitud, Actualidad, Validez, Unicidad, Trazabilidad) en verde/amarillo/rojo.
4. Alcance 1.2 promete "hallazgos, gaps y plan de mejora" pero la plantilla no tiene esa sección. 1.2 lista 5 dimensiones y 3.1 usa 7.

## Regla: no escribir nada que no sepamos → consultar
### Preguntas abiertas al usuario
- [ ] ¿Evaluamos las 15 fuentes o solo las 6 del TP1?
- [ ] Integrantes, legajos, roles y fecha de entrega.
- [ ] ¿Hay Parte B del Entregable 2?
- [ ] ¿Gráficos en anexo del Word, HTML aparte, o ambos?
- [ ] ¿Agregamos la sección de hallazgos/gaps/plan de mejora aunque la plantilla no la tenga?
- [ ] ¿Tenemos el script `calculo_dead_stock.py` (y `verificacion_hallazgos.py`)? No están en las carpetas; sin eso no se puede re-verificar 661 / $83,9 M / semáforo.

### Discrepancias a decidir (detalle en HALLAZGOS_EDA.md §4)
- [ ] D1 Estacionalidad del TP1 (143 vs 61) es efecto del crecimiento; ajustada por tendencia no hay estacionalidad. ¿Cómo lo presentamos?
- [ ] D2 "Cobertura mejoró 10,6→5,2" es efecto del crecimiento; con otras medidas está plana (~5,2).
- [ ] D3 6 tiendas con ventas antes de su fecha de apertura (T25 $776 M, T07 $391 M…). ¿Cuál es el dato correcto?
- [ ] D4 Ventas negativas = devoluciones 1 a 1, pero solo 20% son de clientes (contradice lo que dijo el negocio). ¿Cambiamos el tratamiento (hoy se llevan a 0)?
- [ ] D5 Las 8 fechas "no parseables" de Liquidaciones son válidas (formato con hora). ¿Las recuperamos?
- [ ] D6 stock_en_transito ~20x mayor que lo que explican las Transferencias. ¿Qué incluye el tránsito?
- [ ] D7 Ventas calculadas con precio actual, no con Historial_Precios.
- [ ] D8 Varias fuentes llegan a 2026 y Ventas/Stock terminan en dic-25. ¿Corte de análisis = dic-25?
- [ ] D9 Costo almacenamiento 1,5% (dataset) vs 2% (TP1, confirmado por negocio). ¿Cuál usamos?
- [ ] D10 Duplicados TP1 5.1 (2.135 / 803) no se reproducen (da 2.322 / 811 en ventas).
- [ ] D11 79/93 liquidaciones "Discontinuación" de SKUs activos; 278/496 sin stock ese mes.
- [ ] D12 "Ticket medio" del TP1 es precio medio por unidad.
- [ ] D13 TP1 dice que faltan datasets que ya llegaron.

## Recordar
- Aplicar lecciones del feedback TP1 (`01-reglas-de-entrega.md` §5).
- Las discrepancias que tocan el TP1 ya están anotadas en `02-correcciones-tp1.md` (sección "Detectadas en el EDA del TP2") para el próximo consolidado.
