# Entregable 4 · Entrega final (Grupo 1)

Todo lo que se entrega al cierre de la materia está en esta carpeta. Integra los Entregables 1, 2 y 3 con las correcciones de la cátedra y de Casa Óga. Se armó entre el 22 y el 23-11-2026.

> **Si solo vas a mirar:** abrí `Casa_Oga_Informe_Final_Grupo_1.pdf`, `Presentacion/Casa-Oga-Presentacion-Final.pptx` y `Casa-Oga-Dashboard.html` (doble clic; funciona sin internet).
> **Si vas a cambiar algo:** no edites el Word, el PowerPoint ni el HTML a mano. Se generan con scripts: cambiá el script y regenerá (ver «Cómo regenerar»).

---

## Qué se entrega

| Archivo | Qué es | Generado por |
|---|---|---|
| `Casa_Oga_Informe_Final_Grupo_1.docx` / `.pdf` | **Informe final consolidado** (21 págs.): E1 + E2 + E3 corregidos, más la sección 12 «Cambios respecto de lo entregado» | `Informe/armar_informe_final.py` (+ `Informe/graficos_informe.py` para los 4 gráficos) |
| `Presentacion/Casa-Oga-Presentacion-Final.pptx` | Presentación oral de negocio para Casa Óga: 15 diapositivas (~15 min) con demo del dashboard y notas del orador por integrante | `Presentacion/armar_presentacion_final.js` (usa las capturas de `Presentacion/capturas/`) |
| `Presentacion/Speech-Presentacion-Final.md` | Guion: quién habla en cada diapositiva y qué dice | copiado de las notas del pptx |
| `Presentacion/Preguntas-Jurado.md` | Preparación de la ronda de preguntas: 21 preguntas probables, quién responde cada una, cifras con su sección del informe y frases para temas fuera de alcance | a mano, desde el informe final |
| `Casa-Oga-Dashboard.html` | **Dashboard por área** con la lista de alertas de **agosto de 2026**: filtros, gráficos, tablas y descarga en CSV | `Dashboard/preparar_datos_dashboard.py` → `Dashboard/armar_dashboard.py` |

### Contenido del informe

| § | Sección | Viene de |
|---|---|---|
| — | Resumen ejecutivo y resultados clave | nuevo |
| 1-2 | Contexto, problema, objetivos, stakeholders, restricciones | E1 corregido |
| 3 | Visión, alcance, backlog, plan, **3.5 Metodología (CRISP-DM + Scrum)**, **3.6 Tablero por área** | E1 corregido + nuevo |
| 4 | Fuentes, calidad (13 hallazgos), dataset v4, **4.4 Analítica descriptiva** | E2 |
| 5 | Modelo: métrica, candidatos, selección, punto de operación, resultados 2025/2026, explicabilidad, ficha | E3 rehecho sobre v4 |
| 6-9 | Factibilidad técnica, económica (dos ROI), legal; riesgos y limitaciones | E3 corregido |
| 10 | Diseño de la solución, monitoreo, go-live y **10.4 La primera lista: agosto de 2026** | E3 + nuevo |
| 11 | Veredicto integrado | — |
| 12 | **Cambios** respecto de lo entregado en E1, E2 y E3 (exigido por la cátedra) | — |
| Anexo | Fuentes externas y reproducibilidad | — |

### Vistas del dashboard

| Vista | Para quién | Qué muestra |
|---|---|---|
| Resumen | Dirección | KPIs, flujo vs regla mes a mes, alertas por región y por acción |
| Tiendas | Operaciones / tiendas | Lista de cada tienda ordenada por capital, cupo de 25, acción sugerida y destino de la transferencia |
| Lista de alertas | Todos | Búsqueda, orden por columna, CSV de lo filtrado |
| Compras y categorías | Compras | Capital por categoría y proveedor; SKUs en alerta en varias tiendas |
| Economía | Finanzas | Los dos ROI (2025/2026), valor neto vs cantidad de alertas, sensibilidad |
| Modelo | Quien mantenga el modelo | Recall por cupo, precisión por tramo vs punto de equilibrio, importancia de variables, recall por segmento, ficha |

Los filtros de arriba (región, tienda, categoría, proveedor, origen, acción, dentro del cupo) aplican a todas las vistas. El HTML **no corre el modelo**: muestra resultados ya calculados y embebidos. Para actualizar la lista hay que regenerarlo.

---

## Alcance y decisiones de esta entrega

- **Dataset v4** (`Datasets_Modelo/dataset_entrenamiento_v4*`): 201.310 filas SKU–tienda–mes × 60 variables, 3,22% positivos. El Entregable 3 había usado la v3; acá se reentrenó todo sobre la v4.
- **Target:** cobertura > 12 meses en t+3, sin discontinuados.
- **Partición:** train ≤ dic-24 · validación abr–sep-25 · test ene–may-26. El modelo se elige en una validación interna 2024, así que la validación 2025 queda independiente.
- **Modelo:** HistGradientBoosting solo. El ensamble del E3 no le ganó en la validación interna.
- **Flujo de alertas:** bloque A, la regla (cobertura > 12 hoy), más bloque B, las **150 posiciones** de mayor score del modelo fuera de A. El cupo de 150 lo fija el valor: se suman tramos de 50 mientras la precisión del tramo supere el punto de equilibrio de **11,8%** (VP USD 16,51, FP USD 2,20).
- **Resultados:**
  - Validación 2025: el flujo acierta **404** casos contra **354** de la regla con el mismo cupo.
  - Test 2026: **1.475** contra **1.452**; gana por poco.
- **Economía:** se presentan dos ROI, la automatización de la lista con la regla y el incremental del modelo. En un año como 2025, el ROI a 3 años del total es **+18,6%**, con recupero en unos 24 meses.
- **Lista de ago-26 (dashboard):**
  - Modelo reentrenado con todo lo etiquetado (mar-22 a may-26).
  - **1.016 alertas** (866 regla + 150 modelo) por ARS 189,1 M a costo.
  - 826 transferir / 190 liquidar.
- **Hallazgo de capacidad (§10.4):** en 2026 la regla sola (866) ya supera la capacidad de las tiendas (28 × 25 = 700).
  - Dentro de cada tienda se prioriza por capital: las 700 alertas dentro del cupo concentran el 93% del capital.
  - Queda una decisión para la Dirección: limpieza puntual antes del piloto o ponerse al día en 2-3 meses.
- **Acciones sugeridas:** son reglas simples, no salen del modelo, y la tienda decide.
  - Transferir si otra tienda vende el SKU rápido; congelar compra si hay OC pendientes; si no, liquidar.
- **Costos:** el dashboard muestra costos. La versión para tiendas tendría que publicarse sin esa columna.

**Fuera de alcance / pendiente:**
- Respuestas de Casa Óga a la **Ronda 3** (`Entregable 3/Preguntas-Factibilidad-Ronda-3.xlsx`): no están en el repo. El informe las deja como condición previa al piloto.
- La presentación es un pitch de negocio a Casa Óga, no una exposición técnica. Muestra el dashboard (capturas) y el hallazgo de capacidad; el detalle técnico y la sección «Cambios» quedan en el informe.

---

## Estructura de la carpeta

```
Entregable 4/
├── README.md                              ← este archivo
├── Casa_Oga_Informe_Final_Grupo_1.docx    ← informe final (se genera)
├── Casa_Oga_Informe_Final_Grupo_1.pdf     ← exportado desde Word
├── Casa-Oga-Dashboard.html                ← dashboard autocontenido (se genera)
├── Modelo/
│   ├── modelo_final_v4.py                 ← reentrena y evalúa todo sobre v4; fuente de TODAS las cifras del modelo
│   └── resultados/modelo_final_v4_resultados.json (+ log)
├── Informe/
│   ├── armar_informe_final.py             ← arma el .docx (textos y tablas están en el script)
│   ├── graficos_informe.py                ← 4 gráficos del informe
│   └── graficos/
├── Dashboard/
│   ├── preparar_datos_dashboard.py        ← modelo de producción, scoring de ago-26, acciones, datos por tienda
│   ├── datos_dashboard.json               ← salida del anterior
│   ├── dashboard_plantilla.html           ← HTML/JS/CSS del dashboard (placeholder __DATOS__)
│   └── armar_dashboard.py                 ← inyecta el JSON en la plantilla
└── Presentacion/
    ├── armar_presentacion_final.js        ← genera el .pptx y el speech (pptxgenjs)
    ├── capturas/                          ← capturas del dashboard (tema claro, Edge headless) usadas en la demo
    ├── Casa-Oga-Presentacion-Final.pptx
    ├── Speech-Presentacion-Final.md
    └── Preguntas-Jurado.md                ← preparación de la ronda de preguntas
```

---

## Cómo regenerar (desde la raíz del repo)

Requisitos:
- Python 3.11+ con `pandas`, `numpy`, `scikit-learn`, `lightgbm`, `pyarrow`, `python-docx`, `matplotlib` y `pymupdf`.
- Microsoft Word, para exportar el PDF.
- Node con `pptxgenjs`, solo si se regenera la presentación.

| Paso | Comando | Cuándo |
|---|---|---|
| 1. Modelo | `python "Entregable/Entregable 4/Modelo/modelo_final_v4.py"` | Si cambia el dataset o la configuración del modelo (tarda varios minutos) |
| 2. Gráficos | `python "Entregable/Entregable 4/Informe/graficos_informe.py"` | Después de 1 |
| 3. Filas a puntuar | `EXPORTAR_SCORING=1 python "Entregable/Entregable 2/Modelo/construir_dataset_modelo.py"` | Cuando llega un mes nuevo de datos. Genera `Datasets_Modelo/dataset_scoring_v4.parquet` (último mes con stock) |
| 4. Datos del dashboard | `python "Entregable/Entregable 4/Dashboard/preparar_datos_dashboard.py"` | Después de 1 y 3 |
| 5. Dashboard | `python "Entregable/Entregable 4/Dashboard/armar_dashboard.py"` | Después de 4, o si se toca la plantilla |
| 6. Informe | `python "Entregable/Entregable 4/Informe/armar_informe_final.py"` | Después de 1 y 4 (el §10.4 lee `datos_dashboard.json`). Luego exportar a PDF desde Word |
| 7. Presentación | `node "Entregable/Entregable 4/Presentacion/armar_presentacion_final.js"` (ver encabezado del script) | Si cambian cifras o diapositivas |

**Qué editar según lo que quieras cambiar:**

| Quiero cambiar… | Editar |
|---|---|
| Un texto o una tabla del informe | `Informe/armar_informe_final.py` |
| Una cifra del modelo, el cupo o el ROI | `Modelo/modelo_final_v4.py` (y regenerar 1 → 2 → 6) |
| Las reglas de acción, el cupo por tienda (`CAP_TIENDA = 25`) o las señales | `Dashboard/preparar_datos_dashboard.py` |
| Gráficos, filtros o vistas del dashboard | `Dashboard/dashboard_plantilla.html` (y correr el paso 5) |
| Una diapositiva o las notas | `Presentacion/armar_presentacion_final.js` y el `Speech-Presentacion-Final.md` |

`construir_dataset_modelo.py` sin `EXPORTAR_SCORING` hace exactamente lo mismo que antes y no toca el dataset v4.
