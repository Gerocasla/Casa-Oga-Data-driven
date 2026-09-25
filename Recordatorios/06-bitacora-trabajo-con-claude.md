# Bitácora del trabajo con Claude (17-08 al 25-09-2026)

> Resumen estructurado de la conversación de trabajo con Claude Code, para retomar sin perder contexto después de limpiar la sesión. **No es una transcripción literal**: recoge las decisiones, los números verificados, los hallazgos, los archivos generados y lo que quedó pendiente.
> Leer junto con `00-contexto-proyecto.md`, `04-tp2-eda-pendientes.md` (parcialmente desactualizado, ver §7) y `05-decisiones-modelo.md`.

---

## 1. Cómo retomar (lo primero que hay que saber)

- **Datos a usar:** `Datasets_Normalizados/` · corte de análisis **agosto 2026** · 15 fuentes.
- **Criterios de limpieza vigentes** (definidos por el negocio en la ronda 2):
  - Duplicados por clave (mes, tienda, SKU): **conservar la primera ocurrencia**. Con cualquier otro criterio (p. ej. "mayor venta") los totales no cierran: da $32.621,2 M en vez de $32.538,4 M.
  - Stock negativo: **piso en 0** (error de sincronización POS–inventario, confirmado).
  - Ventas negativas (devoluciones): **netear** contra la venta del mismo SKU-tienda-mes. Antes se llevaban a 0.
  - 22 SKUs sin costo: **costo de OC × 1,2321** (supuesto del proyecto, declarado).
  - Descuentos fuera de rango (5): **excluir** del margen. Presupuesto en cero (ene-may 2022) y negativo (3): **excluir** del desvío.
  - Historial de precios: **no usarlo** para revaluar ventas; manda `precio_lista` del catálogo.
- **Estado de los entregables:**
  - Entregable 2 · Parte A — completo pero con **corte dic-2025** (desactualizado).
  - Entregable 2 · Parte B — **1.1 y 1.2 completas** con corte ago-2026; **1.3 y Sección 2 sin hacer**.
- **Scripts reproducibles** en `Entregable/Entregable 2/EDA/`: `eda_2026.py`, `calidad_2026.py`, `factor_costo_oc.py`, `candidatos_target.py` (los logs quedan en `resultados/`).
- **Identidad de git** configurada solo en este repo: `Santiago Hernandez / sanhernandez@itba.edu.ar`.

---

## 2. Preferencias de trabajo acordadas

- **Respetar la plantilla de cada entregable.** No agregar secciones que la plantilla no trae. (Se agregó una Sección 4 en la Parte A y se sacó a pedido.)
- **No escribir nada que no se pueda justificar** con el EDA, los datos o los entregables anteriores. Se auditaron los 87 números de la Parte A contra `HALLAZGOS_EDA.md`.
- **Textos cortos.** Si se pide "tal cual está en el MD", no reescribir ni ampliar.
- Cuando se pide un archivo concreto (p. ej. `preview.html`), **editar ese y no otro**.
- Responder la pregunta que se hizo; no ofrecer menús de recortes cuando la pregunta es "¿está bien?".
- Las correcciones del feedback de un TP se **tienen en cuenta** en el TP siguiente; en los consolidados se aplican y se registran en la sección "Cambios".

---

## 3. Cronología

### 17-08 · Entregable 1 · Parte B (objetivos, stakeholders y restricciones)
- Se completó a partir de `Respuestas Grupo 1.xlsx`. La primera lectura cortó en la pregunta 23; en realidad eran **45**, y la versión v2 incorporó las 24-45: costo de almacenamiento entregado, piloto por categoría, explicabilidad obligatoria y criterios de calidad de datos.
- Se generó `Preguntas-abiertas-para-validacion.docx`.
- **Hallazgo:** el catálogo tiene **7 categorías reales** (Decoración, Textil hogar, Cocina y mesa, Muebles, Baño, Organización, Iluminación). **"Regalos" no existe**, aunque el negocio la menciona como categoría estacional y la propuso para el piloto. Además Decoración es la categoría más vendedora (21,7%), así que no encaja en el criterio de "baja contribución" con el que la eligieron.

### 27-08 · Clonado del repo y segunda ronda de respuestas
- `Respuestas Grupo 1 al 18-8.xlsx` sumó 9 preguntas (46-54): semáforo 30/70 aprobado como versión inicial; acceso a transferencias; se enviarán datos de 2026; costo de mantener stock **5% mensual** (rango 4-6%); stock en tránsito = stock entrante, **excluirlo** del disponible; existen quiebres de stock; no hay repositorio centralizado; solución **open source liviana** para el piloto (cloud recién en fase 2).
- Se redactó un mail formal pidiendo el dataset de 2026 y el de devoluciones.

### 29-08 · Revisión del diseño de dashboard (Entregable 1 · Parte D)
- **El semáforo 30/70 no es accionable:** el sell-through mensual tiene mediana 15,3%; con ese corte el 74%-86% del catálogo queda en rojo (según fórmula), contra una capacidad de 420-700 intervenciones por mes (28 tiendas × 15-25).
- Criterio de **stock excedente** (propuesto por Santiago): run rate = venta 12 m / 12; excedente = stock − run rate × C. Con C = 6 → $569 M; con C = 12 ("stock muerto proyectado") → $39,6 M. Inactividad y excedente marcan poblaciones **casi disjuntas** (solo 94 posiciones en común): hay que usar los dos ejes.
- El excedente agregado por SKU mostró que el problema es **de compra, no de tienda** (SKU00417 con excedente en 17 de 28 tiendas; 20 SKUs explican el 28% del excedente).
- KPIs de la Parte D: 3 de 5 tenían errores (fórmula de liquidaciones invertida; fórmula y umbrales de días de inventario; umbrales de facturación desconectados de la escala real) y ninguno medía dead stock.
- Artifact publicado: **Semáforo de Dead Stock** — https://claude.ai/code/artifact/ad33622c-dfb9-4e5b-9bad-c481a810d3f7 · HTML y PDF en `Entregable/Entregable 1/`.

### 30-08 · MD nuevos del grupo y Parte D v2
- `minianalisiskpis.md` define dead stock como OR de 3 condiciones (≥3 meses sin venta · stock muerto proyectado > 0 · discontinuado con stock) y reporta **431 posiciones / $34,2 M**. **No se pudo reproducir:** con la definición escrita da **620**; el propio texto dice que las condiciones 2 y 3 "casi duplican" la cobertura, lo que encaja con 620 y no con 431.
- Se reprodujo el universo (**7.993 posiciones con stock a dic-2025**) y el 73,6% de rojo del semáforo 30/70 (fórmula unidades / stock).
- Se generó la **Parte D v2** con los números del MD, a pedido. Commit `97fa23a`, más la carpeta `Cambios/`.

### 30/31-08 · Panel de Dead Stock (HTML del grupo)
- El panel reporta **661 posiciones / 8,27% / $83,9 M / $7,68 M por mes**: contradice al MD (431) y se acerca a la reproducción (620). **661 / $83,9 M son las cifras insignia vigentes del TP1, pero no son reproducibles** (ver §7).
- **Pestaña de tiendas: las diferencias entre tiendas son ruido.** Desvío observado 1,21 pp contra 1,63 pp esperados por azar; chi² 15,6 con 27 gl; correlación con m² −0,17; solo T09 fuera de ±2σ. Implicancia para stakeholders: la expectativa de Lucía O. ("mover stock a tiendas con mejor rotación") no tiene sustento; la palanca está en Compras (Diego P.).

### 31-08 · Pestaña Evolución (sección de Santiago, archivo `preview.html`)
- Recomendaciones de formato; se explicó "capital por posición" y la alternativa "capital muerto como % del stock" (3,05% → 2,38%, pero los promedios anuales quedan planos en ~2,57%).
- Santiago eligió el encuadre de **alarma**: 2025 costó **$102 M** en sostener stock parado ($44,7 M en 2023); 11 de 12 meses de 2025 por encima del promedio 2023-24; pico de **$149,1 M** en agosto 2025 (3,6× el promedio de 2023).
- Cambios aplicados en `preview.html` (carpeta local, **no está en el repo**): bloque de conclusión arriba, textos al pie más cortos, eje X solo con el mes, KPI "Costo de sostenerlo en 2025", pico comparado contra 2023 y gráfico de capital primero. La línea de referencia se probó y se sacó a pedido.
- Se descartó afirmar "el problema creció más rápido que el negocio" (2,28× vs 2,13×: diferencia dentro del ruido).
- Guion para presentar: `Guion-Presentacion-Evolucion.pdf` (carpeta local).

### 20-09 · Entregable 2 · Parte A
- Completada sobre la plantilla: tabla 2.3 (24 filas), matriz 3.1 (15 fuentes × 7 dimensiones) y anexo con los 12 gráficos del EDA.
- Estacionalidad (D1) y cobertura (D2) presentadas con el dato corregido **sin mencionar que contradicen al TP1**: ajustada por tendencia, no hay estacionalidad (índice 101-105); la cobertura está **plana en ~5,2 meses**.
- Correcciones de consistencia: 800 SKUs en catálogo / 798 con ventas; 8.073 posiciones con venta / 7.993 con stock; 7 dimensiones también en el alcance 1.2.
- Commit `9be5c39`.

### 22-09 · Datos a agosto 2026 y Parte B (1.1 y 1.2)
- Segunda entrega de datasets: los mismos archivos con 2026 agregado. **El tramo 2022-2025 quedó idéntico** ($32.538,4 M y 750.538 unidades).
- **EDA de 2026** (`eda_2026.py`), ene-ago 2026 contra el mismo período de 2025: venta **−13,2%**, unidades **−12,7%**, posiciones **−8,1%**. Quiebre brusco de dic-25 a ene-26 (−564 posiciones); después, recuperación mes a mes.
- **Los datos de 2026 no tienen ninguno de los problemas de calidad** del tramo anterior (0 duplicados, 0 negativos, 0 nulos).
- `PROBLEMAS-CALIDAD-DATOS.md` con H1-H12 y R1-R2. Parte B 1.1 y 1.2 completas. Commit `cf8a461`.

### 23 al 25-09 · Variable objetivo y respuestas del negocio (ronda 2)
- El grupo definió el target (`05-decisiones-modelo.md`): **cobertura > 12 meses dentro de 3 meses**, sin discontinuados.
- Llegaron las respuestas P1-P32 (costos, historial, stock negativo, devoluciones, descuentos y presupuesto). Qué cambió:
  - **Neteo de devoluciones** → target recalculado: **3.509 → 4.428 positivos (2,67% → 3,38%)**. El cambio se concentra en posiciones de ~1 unidad/mes. La elección del target se mantiene (recall de la regla trivial 32,5% contra 41,8% y 42,2% de los descartados).
  - **Factor de costo 1,2321** para los 22 SKUs: el stock de esos SKUs a ago-2026 pasa de $58,7 M a **$72,3 M**.
  - **El historial de precios es una reconstrucción** hecha una sola vez para el proyecto: el sistema pisa el precio y no guarda historia.
  - **No deflactar la venta por IPC:** `venta_neta` ya está valuada aproximadamente al precio actual (85%-99% del precio de lista en todo el período). Para comparar años, usar unidades.
  - H2 (SKUs duplicados) confirmado como **error del sistema**. Stock negativo confirmado como **error de sincronización**. Los motivos de devolución quedan explicados ("sin rotación" = devolución al proveedor).
- Documentos actualizados: Parte B (hallazgos, mapa, plan, supuesto declarado y sugerencias pedidas por el negocio), `PROBLEMAS-CALIDAD-DATOS.md` y `05-decisiones-modelo.md`.

---

## 4. Números de referencia vigentes

| Métrica | Valor | Base |
|---|---|---|
| Venta total 2022-2025 | $32.538,4 M · 750.538 uds | limpio, 1ra ocurrencia |
| Venta total 2022 - ago-2026 | $40.499,8 M · 934.534 uds | idem |
| Venta por año | 2022 $1.812 M · 2023 $6.323 M · 2024 $10.669 M · 2025 $13.734 M · 2026 (8 m) $7.961 M | |
| Posiciones con stock | 7.993 (dic-25) · 7.479 (ago-26) | |
| Cobertura agregada | ~5,2 meses estable 2023-2025 · 4,95 a ago-26 | |
| Pareto | 248 de 798 SKUs = 80% de la venta | |
| Margen teórico de lista | 44,9% | |
| Costo de mantener stock | 5% mensual (2% almacenaje + 3% oportunidad), rango 4-6% · dataset dice 1,5% de almacenaje | negocio / dataset |
| Target (cobertura > 12 a 3 meses) | 4.428 / 131.189 = 3,38% · tasa 2,0% (2023-25) vs 9,0% (2026) | neteo |
| Dead stock TP1 (panel) | 661 posiciones · $83,9 M · $7,7 M/mes | **no reproducible** |
| Capacidad operativa | 420-700 intervenciones/mes (15-25 por tienda) | **nunca medida** |

---

## 5. Archivos generados o modificados en este trabajo

| Archivo | Qué es |
|---|---|
| `Entregable/Entregable 1/Entregable-1-ParteB-...docx` | Parte B del TP1 |
| `Entregable/Entregable 1/Entregable-1-ParteD-Diseno-Dashboard-v2.docx` | Parte D v2 (números del MD de agosto) |
| `Entregable/Entregable 1/Semaforo-Dead-Stock-Casa-Oga.html` / `.pdf` | Análisis de calibración del semáforo |
| `Entregable/Entregable 1/Preguntas-abiertas-para-validacion.docx` | Preguntas de validación, ronda 1 |
| `Entregable/Entregable 2/Entregable 2 - Parte A - COMPLETADO.docx` | TP2 Parte A (corte dic-25) |
| `Entregable/Entregable 2/Entregable 2 - Parte B - COMPLETADO.docx` | TP2 Parte B, 1.1 y 1.2 (corte ago-26) |
| `Entregable/Entregable 2/PROBLEMAS-CALIDAD-DATOS.md` | Registro de hallazgos de calidad |
| `Entregable/Entregable 2/EDA/eda_2026.py` | EDA del período 2026 |
| `Entregable/Entregable 2/EDA/calidad_2026.py` | Chequeos de calidad al corte ago-26 |
| `Entregable/Entregable 2/EDA/factor_costo_oc.py` | Factor de ajuste del costo de OC |
| `Entregable/Entregable 2/EDA/candidatos_target.py` | Comparación de targets (ahora con neteo; `CRITERIO_NEG=clip` reproduce el anterior) |
| `Cambios/2026-08-30_1459_actualizacion-parte-D.md` | Registro de la actualización de la Parte D |

**Fuera del repo** (carpeta local `Data Driven/`): `preview.html` con la pestaña Evolución modificada, `Panel-Dead-Stock-CasaOga*.html` y `Guion-Presentacion-Evolucion.pdf`.

---

## 6. Hallazgos que conviene tener presentes en los próximos entregables

1. **La venta cae 13,2% en 2026** después de tres años de crecimiento. Todavía no figura en ningún documento. Además explica la inestabilidad del target: si cae la venta y el stock no acompaña, la cobertura sube y más posiciones cruzan los 12 meses.
2. **El dead stock es un problema de producto y de compra, no de tienda.** Las diferencias entre tiendas no son estadísticamente significativas.
3. **No hay estacionalidad** una vez descontado el crecimiento, aunque el negocio la percibe.
4. **La cobertura está estable**, no "mejoró de 10,6 a 5,2" (eso era un efecto de cálculo del TP1).
5. **"Regalos" no existe** en el maestro de productos.
6. **Seis tiendas venden antes de su fecha de apertura** (11.058 filas, $1.471,7 M): afecta cualquier variable de antigüedad de tienda.

---

## 7. Pendientes

**Entregable 2**
- [ ] Parte B **1.3**: dashboard antes/después. El "antes" son los datos crudos; el "después", los criterios de la §1.
- [ ] Parte B **Sección 2**: 2.1 (dataset de entrenamiento: casi todo definido en `05-decisiones-modelo.md`) y 2.2 (transformaciones).
- [ ] **Actualizar la Parte A al corte ago-2026**, para no entregar dos partes del mismo TP con cortes distintos.
- [ ] Carátula: legajos de Simón Volpato Escandarani y Santiago Hernández, fecha y roles.
- [ ] Actualizar `04-tp2-eda-pendientes.md`: varias preguntas ya se respondieron (15 fuentes, respetar plantilla, gráficos en anexo, corte ago-2026, 2026 = segunda entrega).

**Decisiones del equipo**
- [ ] ¿Excluir del neteo el motivo "sin rotación" (devolución al proveedor, ~21% de las unidades devueltas)? El negocio reconoce que es un movimiento de inventario y no una venta.
- [ ] El factor de costo contradice en parte al negocio: en los otros 766 SKUs el costo de OC coincide con el de catálogo (mediana 0,999). Se aplicó igual, como se pidió.

**Con el negocio**
- [ ] Nunca preguntado: **H3** ventas antes de la apertura · **H6** qué incluye el stock en tránsito · **H12** extensión a 2026 de Devoluciones, Calendario y Catálogo.
- [ ] Sin respuesta: **H7** liquidaciones por discontinuación sobre SKUs activos y tienda "Todas" · **H10** promociones duplicadas y con fechas invertidas · cumplimiento presupuestario uniforme (~91%).
- [ ] Aprobación del target, los cortes y las acciones por banda (María G.); visto bueno de Carlos F.; confirmación de la capacidad de 15-25 intervenciones por tienda (Lucía O.).

**TP1 / consolidado**
- [ ] `calculo_dead_stock.py` no existe: las cifras 661 / $83,9 M / semáforo 345-652 no se pueden reproducir. Hay tres números en circulación para la misma métrica (431, 620 y 661).
- [ ] Correcciones del feedback del TP1 (`02-correcciones-tp1.md`) sin aplicar al consolidado.
- [ ] En `Cambios/` conviven versiones viejas y nuevas de los MD de análisis (con y sin guiones en el nombre); las viejas tienen cifras desactualizadas.
