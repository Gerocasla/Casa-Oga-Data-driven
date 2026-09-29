# Entregable 2 — Estado y pendientes

> Actualizado 28-09-2026. Versión anterior (preguntas abiertas del 20/22-09) en el historial de git; casi todas quedaron respondidas.
> Checklist contra las diapositivas de la Unidad 2: `07-checklist-unidad-2.md`.

## Datos
- Usar `Datasets_Normalizados/` · corte **ago-2026** · 15 fuentes. `Datasets/` queda intacta.
- Dataset del modelo: `Datasets_Modelo/dataset_entrenamiento_v3*` (lo genera `Entregable 2/Modelo/construir_dataset_modelo.py`).
- Criterios de limpieza vigentes: ver `06-bitacora-trabajo-con-claude.md` §1 y `Material/Respuestas-Ronda-2-Calidad-de-Datos.md`.

## Estado por parte

| Parte | Sección | Estado |
|---|---|---|
| A | Carátula | ❌ Faltan legajos de Simón y Santiago, roles y fecha |
| A | 2.3 EDA + anexo | ✅ 28-09 · recalculada al **corte ago-2026** (`EDA/eda_ago26.py`, gráficos en `EDA/graficos_ago26/`) |
| A | 3.1 Matriz de calidad | ✅ 28-09 · actualidad en rojo para Devoluciones, Calendario y catálogo |
| B | Carátula | ❌ Legajos de Simón y Santiago, roles de Gerónimo, Gianfranco, Matías y Simón, fecha |
| B | 1.1 Hallazgos y mapa | ✅ |
| B | 1.2 Plan de mejora | ✅ (incluye supuesto de costo y sugerencias pedidas por el negocio) |
| B | 1.3 Dashboard antes/después | ✅ 28-09 · `Dashboard-Calidad-Antes-Despues.html` + tabla de 11 métricas |
| B | 2.1 Dataset de entrenamiento | ✅ 28-09 · **v3: 60 features, universo 3+ meses**, tabla de fuentes, riesgos de sesgo y tabla de variables excluidas |
| B | 2.2 Transformaciones | ✅ 28-09 |
| — | Dashboard | ✅ 28-09 · 5 pestañas con insights |
| — | Presentación | ✅ 28-09 · v1 completa (34) y v2 corta (14), HTML + PDF |

## Preguntas que ya se respondieron (antes estaban abiertas acá)
- 15 fuentes, no solo las 6 del TP1 · Sí hay Parte B · Gráficos en el anexo del Word · Respetar la plantilla (no agregar secciones) · Corte de análisis ago-2026 · Scripts `calculo_dead_stock.py` / `verificacion_hallazgos.py`: no existen.
- D4, D5, D7, D8, D9 (parcial), D10, D12, D13: resueltas o incorporadas como hallazgos H1-H12.

## Pendientes

**Para cerrar el Entregable 2**
- [x] Parte A al corte ago-2026 (28-09).
- [x] Presentación en un solo archivo, dos versiones para elegir (`Entregable 2/Presentacion/`): **v1 completa** (34 diapositivas) y **v2 corta** (14), cada una en HTML y PDF. Cómo se genera: `Presentacion/README.md`. La v1 también está online y editable: https://claude.ai/artifact/3ggL4DDAvfEwxBzwtHLVso (privada; compartir desde Share).
- [ ] **Elegir versión de la presentación** (v1 completa o v2 corta) según el tiempo que den para exponer.
- [x] Dashboard ampliado a 5 pestañas (`Modelo/insights_dashboard.py` + `Modelo/armar_dashboard.py`).
- [ ] Carátulas (legajos, roles, fecha).
- [ ] Decidir si se excluye del neteo el motivo "sin rotación" (devolución a proveedor, ~21% de las unidades devueltas). Hoy se netea todo (default P23).
- [ ] Revisar con el grupo el dataset v3 (60 features, universo con 3+ meses de historia, partición con embargo). Si se cambia algo: subir a v4, no pisar.

**Con el negocio (no bloquean la entrega, se declaran como limitación)**
- [ ] Nunca preguntado: H3 (ventas antes de la apertura), H6 (qué incluye stock en tránsito), H12 (Devoluciones, Calendario y Catálogo a 2026).
- [ ] Sin respuesta: H7, H10, cumplimiento presupuestario uniforme.
- [ ] Aprobación del target (María G.). Es lo más importante: la Clase 8 insiste en validar la definición antes de etiquetar.

**Advertencias para el modelado (TP siguiente)**
- La prevalencia del target en 2026 (9,0%) es 4,6 veces la de 2023-2025 (~2%). El test (ene-may 2026) mide robustez ante ese cambio; no comparar métricas de validación y test como si fueran el mismo problema.
- Chequeo de sanidad (28-09): logística y gradient boosting dan AUC ~0,90 en validación y ~0,97 en test; la cobertura actual sola da 0,94 en test. Sin señales de leakage, pero el test de 2026 es "fácil" porque la cola engorda por la caída de venta.
- Con 420 alertas/mes el modelo de prueba captura 58% de los casos vs 47% ordenando por cobertura actual; con 700, 73% vs 57% (validación). Con menos de ~100 alertas la regla es igual o mejor: el modelo aporta en el rango de la capacidad declarada.
- 30 de 55 features numéricas no separan solas (AUC < 0,55). La antigüedad de la posición separa en train (0,61) pero no en 2026 (0,50): no hay productos nuevos en el test porque el catálogo está congelado.
- La caída 2026 (−13,2%) es sobre todo de catálogo: 96 SKUs discontinuados a fin de 2025 explican 8,9 pp; los 634 que siguen caen 4,8% y en jul-ago ya están casi al nivel de 2025. Las posiciones activas con stock y sin venta en 3 meses saltan de 365 a 929 en ene-mar 2026, con liquidaciones −51% (solo 4 de las 929 liquidadas). Números: `EDA/resultados/cambio_2026.json`.
- 2026 no tiene devoluciones → el neteo es asimétrico entre años. La comparación interanual se hace en bruto.
