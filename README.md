# Casa Óga · Proyecto Data Driven (Grupo 1)

Trabajo de la materia **Factibilidad de Proyectos Data Driven** (ITBA, 2C 2026). Caso: **Casa Óga**, retail ficticio de hogar y decoración (28 tiendas + e-commerce).
Frente trabajado: **mix de productos / dead stock** — predecir qué posiciones SKU–tienda van a quedar con stock inmovilizado.

Integrantes: Gerónimo Fasce · Gianfranco Di Claudio · Matías Fleischer · Simón Volpato Escandarani · Santiago Hernández.

> **Para retomar el trabajo:** leé este README y después `Recordatorios/06-bitacora-trabajo-con-claude.md` (§1 «Cómo retomar»).

---

## Estado (actualizado 30-10-2026)

| Entregable | Estado | Archivos |
|---|---|---|
| **1** · Contexto, objetivos, visión, dashboard (Clases 1-4) | Entregado. Feedback recibido; **correcciones sin aplicar** (van al consolidado final) | `Entregable/Entregable 1/`, `Recordatorios/02-correcciones-tp1.md` |
| **2 · Parte A** · EDA y evaluación de calidad | ✅ Completa, corte ago-2026 · **feedback aplicado** (ver `Entregable/Entregable 2/Correcciones-Feedback-Grupo-1.md`) | `Entregable/Entregable 2/Entregable 2 - Parte A - COMPLETADO.docx` |
| **2 · Parte B** · Plan de mejora, dashboard antes/después, dataset de entrenamiento | ✅ Completa · **feedback aplicado**: H13 (2026 con otra fuente), plazos, capital por categoría, dataset v4 | `Entregable/Entregable 2/Entregable 2 - Parte B - COMPLETADO.docx` |
| **2 · Dashboard** | ✅ 5 pestañas · suma capital inmovilizado por categoría | `Entregable/Entregable 2/Dashboard-Calidad-Antes-Despues.html` |
| **2 · Presentación** | ⚠️ Final: **v4 corta modelo** (16) · cifras de v3, sin regenerar tras el feedback (ver Correcciones) | `Entregable/Entregable 2/Presentacion/Casa-Oga-Entregable-2-v4-corta-modelo.html` |
| **2 · Envío a la cátedra** | ✅ Consolidado A+B (v3.0, revisado), presentación, dataset **v4** (CSV), diccionario v4 y dashboard antes/después. Los archivos `*-v3` de la carpeta quedan del envío anterior: no mandarlos | `Entregable/Entregable 2/Envio-Profesores/` (se regenera con los `armar_*.py` de esa carpeta) |
| **3** · Modelado | En curso sobre la **v3** (que se conserva sin cambios) | Pendiente: decidir si se reentrena con la v4; reportar validación 2025 y test 2026 por separado con la regla «cobertura > 12» como línea base |

**Falta para reentregar el 2:** fecha de reentrega en la carátula del consolidado.
**Pendiente con el negocio (no bloquea):** aprobación del target (María G.), capacidad de 15-25 intervenciones por tienda (Lucía O.), preguntas H3/H6/H12.

---

## Las decisiones centrales, en una tabla

| Tema | Decisión | Por qué |
|---|---|---|
| Datos | `Datasets_Normalizados/`, corte **ago-2026** | 2026 llegó en una segunda entrega; el tramo 2022-25 quedó idéntico |
| Duplicados (H1) | **v4:** conservar el registro de mayor venta por (mes, tienda, SKU); en Stock, el de la misma fila (v1-v3: 1ra ocurrencia) | Regla sugerida por Casa Óga (P4 del relevamiento). Cambia 600 de 2.330 claves y −34 positivos |
| Stock negativo (H4) | Piso en 0 | Error de sincronización POS–inventario (P14-P16) |
| Ventas negativas (H4) | Netear contra la venta del mismo SKU-tienda-mes, **salvo «sin rotación / no vendido» (v4)** | Las de clientes son devoluciones reales (P23); la de proveedor es movimiento de inventario (P18-P19): −330 positivos |
| 22 SKUs sin costo (H11) | Costo de OC × **1,2321** — supuesto declarado | Nivela su margen con el 44,9% del resto (P3-P7) |
| Descuentos y presupuesto inválidos (H9) | Excluir | Error de carga / proceso inmaduro (P24-P32) |
| Historial de precios (H8) | No usar | Es una reconstrucción, no un registro (P9-P10) |
| Comparar años | En unidades o en bruto; **sin deflactar por IPC** | La venta ya está a precio actual; 2026 no trae devoluciones |
| **Target** | 1 si la posición tiene **cobertura > 12 meses en t+3** (stock / promedio 12 m de unidades netas), sin discontinuados | Menos inercia que las alternativas (68% de casos nuevos); ver `Recordatorios/05-decisiones-modelo.md` |
| Unidad / universo | SKU–tienda–mes; stock > 0 en t, no discontinuada, **3+ meses de historia**, t+3 observado | Es donde se decide la acción; con 12 meses quedaban afuera los productos nuevos (40% de las filas) |
| Partición | Temporal con embargo de 3 meses: train mar-22→dic-24 · val abr→sep-25 · test ene→may-26 | La prevalencia salta de ~2,5% a 9% en 2026 |
| Cobertura en el transformado | **v4:** tope 60 meses para el infinito + log1p, **sin winsorizar al p99** (v3: techo 18 meses) | El p99 igualaba el 1,5% de las filas de train y el 26,5% de los positivos; con o sin recorte rinden igual |
| Dataset | **v4**: 201.310 filas × 60 features (55 num + 5 cat), 106 tras one-hot · 3,22% positivos · peso de clase 42,1 (v3: 201.306 · 3,40% · 39,0, se conserva para el Entregable 3) | Todas con información ≤ t; sin precio/costo del catálogo (son el valor de hoy) ni stock en tránsito (H6); exclusiones en Parte B §2.1 |

---

## Estructura del repo

```
Casa-Oga-Data-driven/
├── README.md                      ← este archivo
├── REGISTRO-CAMBIOS-DATASETS.md   ← bitácora de todo lo que se tocó en los datos
├── Datasets/                      ← CSV tal como los entrega la cátedra (NO se editan)
├── Datasets_Normalizados/         ← mismos datos con representación unificada: USAR ESTOS
├── Datasets_Modelo/               ← dataset de entrenamiento v3 (parquet + muestra CSV + diccionario)
├── Entregable/
│   ├── Entregable 1/              ← TP1 entregado (docx, dashboards HTML, semáforo)
│   └── Entregable 2/
│       ├── Entregable 2 - Parte A/B - *.docx   ← consignas y versiones completadas
│       ├── PROBLEMAS-CALIDAD-DATOS.md          ← hallazgos H1-H12, R1-R2 y su tratamiento
│       ├── Dashboard-Calidad-Antes-Despues.html
│       ├── EDA/          ← scripts de EDA y calidad, resultados/ (logs, csv, json), graficos/ y graficos_ago26/
│       ├── Modelo/       ← construcción del dataset, insights, armado del dashboard, resultados/
│       └── Presentacion/ ← generador del deck, gráficos, HTML y PDF finales
├── Material/                      ← respuestas del negocio y diapositivas de la Unidad 2
├── Mejoras/                       ← feedback de la cátedra
├── Cambios/                       ← documentos de análisis del TP1 (históricos)
└── Recordatorios/                 ← notas de trabajo: contexto, reglas, correcciones, decisiones, bitácora
```

---

## Cómo reproducir todo (desde la raíz del repo)

Requisitos: Python 3.11+ con `pandas`, `numpy`, `matplotlib`, `scikit-learn`, `pyarrow`, `python-docx`, `pillow`, `pymupdf`. Microsoft Edge para exportar los PDF.

| Paso | Comando | Genera |
|---|---|---|
| 1. Normalizar | `python "Entregable/Entregable 2/EDA/normalizar_datasets.py"` | `Datasets_Normalizados/` |
| 2. EDA Parte A | `python "Entregable/Entregable 2/EDA/eda_ago26.py"` | `EDA/resultados/eda_ago26.*`, `EDA/graficos_ago26/` |
| 3. Calidad | `python "Entregable/Entregable 2/EDA/calidad_2026.py"` | log de hallazgos H1-H12 |
| 4. Factor de costo | `python "Entregable/Entregable 2/EDA/factor_costo_oc.py"` | factor 1,2321 y costos de los 22 SKUs |
| 5. Candidatos a target | `python "Entregable/Entregable 2/EDA/candidatos_target.py"` | comparación de 5 targets |
| 6. Antes / después | `python "Entregable/Entregable 2/EDA/antes_despues.py"` | métricas de la Parte B §1.3 |
| 7. Dataset | `python "Entregable/Entregable 2/Modelo/construir_dataset_modelo.py"` | `Datasets_Modelo/dataset_entrenamiento_v4*`, señal univariada, perfil t+3, comparación del recorte |
| 7a. Reglas v3 → v4 | `python "Entregable/Entregable 2/Modelo/comparar_reglas_v4.py"` | `Modelo/resultados/comparar_reglas_v4*` |
| 7b. Chequeo de señal | `VERSION_DATASET=v4 python "Entregable/Entregable 2/Modelo/chequeo_senal.py"` | modelos de prueba, curva de capacidad e importancia (`Modelo/resultados/*_v4.csv`) |
| 8. Insights | `python "Entregable/Entregable 2/Modelo/insights_dashboard.py"` | `Modelo/resultados/insights.json` |
| 9. Dashboard | `python "Entregable/Entregable 2/Modelo/armar_dashboard.py"` | `Dashboard-Calidad-Antes-Despues.html` |
| 10. Presentación | `graficos_presentacion.py` → `generar_deck.py` → `armar_html.py` (en `Presentacion/`) | HTML de las dos versiones; el PDF se imprime con Edge (ver `Presentacion/README.md`) |

Los `.docx` se editaron con scripts puntuales de python-docx; si se regeneran los números, actualizar el Word a mano o pedirle a Claude que lo haga.

---

## Material de referencia

- Respuestas del negocio: `Material/Respuestas_Grupo_1.xlsx`, `Material/Respuestas Grupo 1 al 18-8.xlsx`, `Material/Respuestas-Ronda-2-Calidad-de-Datos.md`.
- Diapositivas de la Unidad 2 (clases 6, 7 y 8): `Material/Unidad 2/`. Checklist contra lo hecho: `Recordatorios/07-checklist-unidad-2.md`.
- Presentación online (misma versión completa, editable): https://claude.ai/artifact/3ggL4DDAvfEwxBzwtHLVso — privada, se comparte desde su menú Share.
