# Correcciones pendientes — Entregable 1 (TP1)

- **Fuente:** `Data-Driven\Mejoras\Feedback Grupo 1.xlsx`
- **Documento a corregir:** `Data-Driven\Entregable\Entregable 1\Entregable_1_Consolidado_G1.docx`
- **Resultado del feedback:** 25 secciones → 16 Completo / 9 Revisar (Parte D: todo completo)
- **Estado general:** ⏳ Ninguna corrección aplicada todavía

Al aplicar cada una: marcar `[x]` y anotarla en `03-registro-de-cambios.md`.

---

## Prioridad ALTA

### [ ] 1. Parte B · 1.3 Problem Statement + Sección 5.3 — cifras que no cierran
- La tabla "cuatro caminos independientes" (5.3, compara 2023 vs 2025) dice: % posiciones dead stock **8,86% → 7,93%** y capital inmovilizado **$41,4 M → $93,1 M**.
- El resto del documento (Resumen Ejecutivo, 1.3, OE4, 5.2, Alcance) usa **10,63% (ene-2023) → 8,27%**, cobertura **10,6 → 5,2 meses** y **$83,9 M** a dic-2025.
- **Qué hacer:** recalcular la tabla o explicar explícitamente la diferencia de base de cálculo, y dejar un único juego de cifras reconciliado. Revisar todas las apariciones.
- Cátedra: "la observación más seria de esta revisión".

### [ ] 2. Parte B · 1.3 Problem Statement — narrativa demasiado alarmista
- El PROBLEMA presenta el crecimiento del capital inmovilizado como deterioro, pero el propio análisis (5.3) muestra que el % de dead stock **bajó** y la cobertura **mejoró**; creció solo el monto absoluto, en línea con el catálogo (ventas ×2,13, stock ×2,14).
- **Qué hacer:** incorporar esa aclaración dentro del Problem Statement (mantener estructura CONTEXTO/PROBLEMA/PROPUESTA).

### [ ] 3. Parte C · 2.3 Fases planificadas — falta el Backlog inicial
- El título de la Parte C promete "Backlog inicial" y no existe: solo se menciona "backlog" como herramienta. Las tareas están calendarizadas directo en las Fases 1-4.
- **Qué hacer:** crear un **backlog inicial priorizado** (épicas + historias de usuario, con prioridad), del cual se nutren las fases, aclarando que se refina sprint a sprint. Confusión conceptual "plan de fases vs backlog".

---

## Prioridad MEDIA

### [ ] 4. Parte A · 1.3 Área/proceso bajo análisis — "Proceso clave" mal definido
- Hoy dice: "Identificar anticipadamente los productos con riesgo de convertirse en stock de baja rotación, y definir decisiones de liquidación, transferencia o discontinuación…" → eso es el **objetivo del proyecto** (casi igual a 2.1).
- **Qué hacer:** reemplazar por el proceso real vigente, ej. **"Gestión de rotación y liquidación de inventario"**, describiendo el circuito manual y reactivo actual (detección manual → liquidar / transferir / discontinuar, sin protocolo escrito, caso por caso).

### [ ] 5. Parte A · 1.2 Situación actual del mercado — sin fuente externa
- Solo hay datos internos (estacionalidad 143 dic vs 61 ene, giro estratégico).
- **Qué hacer:** agregar al menos una fuente externa citada (INDEC, cámara sectorial, consultora) que sustente "mayor competencia de precios y apertura importadora" (afirmación usada en el Problem Statement).

### [ ] 6. Parte B · 2.1 Mapa de stakeholders — influencia de Responsables de tienda
- Tienen Influencia "Bajo", pero su capacidad estimada (15-25 intervenciones/mes, nunca medida) dimensiona el semáforo (345 rojo / 652 amarillo) y las 420-700 alertas.
- **Qué hacer:** distinguir **influencia de diseño/técnica (alta)** vs **influencia política/decisión (baja)** — dos columnas o justificación explícita.

### [ ] 7. Parte B · 3.1 Restricciones tecnológicas — reclasificar
- "Calidad y gobierno de datos deficiente" → no es tecnológica; es **hallazgo de factibilidad** (5.1) y está duplicada con 3.4 "Gobierno del dato maestro". Sacar/reubicar.
- "Ausencia de área de datos o IT interna" → restricción de **capacidad organizacional**.
- "Alcance de datos acotado sin e-commerce" → **decisión de alcance** (ya está en la tabla "Dato solicitado"). Quitar de acá.
- "Granularidad temporal mensual" → **está bien**; opcional presentarla como consecuencia de "Sin repositorio centralizado ni integración".

---

## Prioridad BAJA

### [ ] 8. Parte B · 3.2 Restricciones temporales — mal categorizada
- "Disponibilidad limitada de usuarios clave" → es de **RRHH / capacidad de las áreas de negocio**, no temporal. Moverla.

### [ ] 9. Parte C · 1.2 Alcance del proyecto — aclarar que el dashboard no es en vivo
- El bullet "Dashboard liviano para responsables de tienda, Compras y Dirección" puede leerse como herramienta operativa lista.
- **Qué hacer:** aclarar en el Alcance mismo que el dashboard y el análisis descriptivo son un **corte histórico con actualización mensual manual** (hoy solo se explica en Parte D 5.1).

---

## Agregadas por la Clase 7 (errores frecuentes del TP1, 28-09-2026)
No estaban en nuestro feedback, pero la cátedra las pone en el checklist de la **presentación final** (`Material/Unidad 2/Clase 7 - TP1_Errores_Frecuentes.md`, diapositiva 24). Ver `07-checklist-unidad-2.md`.

### [ ] 10. Parte C · 1.1 Visión — la anticipación tiene que estar en el mecanismo
- Verificar que la Visión no prometa más de lo que hace el modelo. El target actual (cobertura > 12 meses **en t+3**, entrenado con features hasta t) sí anticipa, pero el semáforo del dashboard marca el estado **presente**. Si la Visión habla de "anticipar", aclarar que eso lo da el modelo, no el semáforo.

### [ ] 11. Parte B · 1.2 Objetivos específicos — mínimo aceptable
- Cada objetivo tiene que tener un **valor mínimo exigible**, no un rango con condicionales. Si depende de algo que todavía no existe (línea base monetaria, capacidad de 15-25 intervenciones nunca medida), marcarlo como "no medible aún".

### [ ] 12. Parte B · 2.1 Stakeholders — faltan Sistemas/IT y proveedores externos
- El relevamiento de la ronda 2 dice que **el responsable de IT renunció sin dejar documentación** (P3-P4) y que hay un proveedor del POS / del sistema de promociones. Condicionan la parte técnica (H4, H5, H8, H10): tienen que estar en el mapa, en filas separadas si tienen poder de decisión distinto.
- Revisar además que cada expectativa asignada sea trazable al relevamiento; si no, marcarla como supuesto del equipo.

### [ ] 13. Parte D — lo prometido tiene que estar, y vigente
- Todo lo que el texto dice "se adjunta" (mockup, PDF de vistas) tiene que estar en la carpeta de entrega.
- El dashboard del TP1 corta en dic-2025; los datos ya llegan a ago-2026. Aclarar el plan para actualizarlo antes del hito de negocio (cierre de inventario de fin de año).
- Si hay PPTX, que diga lo mismo que el documento.

### Problem Statement (refuerza #1 y #2)
- Orden **de afuera hacia adentro**: impacto de negocio → síntoma operativo → causa técnica.
- Traer la cifra más reciente y directa: **la venta cae 13,2% en ene-ago 2026** contra el mismo período de 2025 (todavía no figura en ningún documento). Aclarar que 2 de cada 3 pesos de esa caída son SKUs discontinuados a fin de 2025; los que siguen caen 4,8%.

---

## Detectadas en el EDA del TP2 (no vienen del feedback, pero afectan al TP1)
Fuente: `Entregable\Entregable 2\EDA\HALLAZGOS_EDA.md` §4. **Pendiente de decisión del usuario antes de corregir.**

- [ ] **D1 · 1.2 / 5.4.1 / 5.4.3 — Estacionalidad:** índice 143 dic vs 61 ene es efecto del crecimiento (normalización por año en un negocio que pasó de 17 a 8.073 posiciones). Ajustado por tendencia: 101-105 todos los meses. También cae "Organización 79 vs 117" y la justificación del corte de 12 meses por temporada alta.
- [ ] **D2 · Resumen / 1.2 / 5.3 — Cobertura "10,6 → 5,2":** solo sale con stock / promedio 12m (distorsionado por el arranque 2022). Con otras medidas: plana ~5,2-5,3. Impacta la corrección #2 (no decir "mejoró", sino "estable").
- [ ] **D10 · 5.1 — Duplicados:** "2.135 con valores distintos / 803 con cero" no se reproduce → Ventas 2.322 / 811; Stock 2.357.
- [ ] **D5 · 5.1 — Liquidaciones:** las 8 fechas "no parseables" son válidas (formato `AAAA-MM-DD 00:00:00`).
- [ ] **D4 · Resumen / 5.1 — Ventas negativas:** coinciden 1 a 1 con Devoluciones_SKU; solo 20% son devoluciones de cliente (el texto dice "mayormente de clientes").
- [ ] **D9 · 1.5 / 2.5.3 — Costo almacenamiento:** dataset dice 1,5% del precio de lista; TP1 usa 2%.
- [ ] **D12 · 1.1 — "Ticket medio $43.353":** es precio medio por unidad, no ticket.
- [ ] **D13 · Resumen / 2.6 / 5.1 / 5.6 — Datasets "no recibidos":** transferencias, promociones, presupuesto, devoluciones, proveedores y costos por categoría ya están disponibles.
- [ ] **D3 · 1.1 / 5.2 — Tiendas:** 6 tiendas con ventas antes de su fecha de apertura (afecta cualquier análisis por antigüedad de tienda).

---

## Secciones marcadas "Completo" (no tocar, salvo arrastre de cifras de #1)
A 1.1, A 1.4 · B 1.1, B 1.2, B 3.3, B 3.4 · C 1.1, C 1.3, C 2.1, C 2.2 · D 1.1, D 1.2, D 2.1, D 3.1, D 4.1, D 5.1, D 6.1
