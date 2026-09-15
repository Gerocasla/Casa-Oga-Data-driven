# Reglas de entrega

## 1. Entrega final de la materia
Al final hay que entregar **un único documento consolidado con TODOS los TPs**, y **dentro de ese mismo documento** una **sección "Cambios"** donde la cátedra pueda ver qué partes fuimos modificando respecto de lo que se entregó originalmente.

## 2. Qué incluir según el tipo de entrega

| Tipo de entrega | ¿Aplicar correcciones de TPs anteriores? | ¿Incluir sección "Cambios"? |
|---|---|---|
| **Entregable nuevo (TP2, TP3, …) solo** | Tenerlas en cuenta (no repetir los errores marcados) | **No** hace falta aclarar modificaciones |
| **Cualquier consolidado** (parcial o final) | **Sí**, todas las correcciones aplicadas | **Sí, siempre** |

## 3. Proceso cada vez que llega un feedback
1. Leer el feedback (queda en `Data-Driven\Mejoras\`).
2. Crear `0X-correcciones-tpN.md` en esta carpeta con cada observación como checklist.
3. Aplicar las correcciones sobre la versión consolidada (guardar como **versión nueva**, nunca pisar el original entregado).
4. Por cada corrección aplicada: marcar `[x]` y registrar el cambio en `03-registro-de-cambios.md`.

## 4. Formato sugerido de la sección "Cambios" del consolidado
Tabla por TP, generada a partir de `03-registro-de-cambios.md`:

| # | TP / Parte / Sección | Qué decía | Qué dice ahora | Motivo (feedback) |
|---|---|---|---|---|

## 5. Lecciones del feedback TP1 para TODOS los próximos entregables
- **Consistencia numérica:** una misma métrica = un mismo valor en todo el documento. Si hay dos cálculos, reconciliarlos explícitamente.
- **No exagerar la urgencia:** si un monto absoluto crece por crecimiento del negocio, decirlo; usar también ratios.
- **Afirmaciones de contexto con fuente externa citada** (INDEC, cámaras, consultoras).
- **Proceso ≠ objetivo:** el "proceso bajo análisis" describe cómo opera HOY la empresa, no lo que el proyecto quiere lograr.
- **Clasificar bien** restricciones/riesgos (tecnológica vs. organizacional vs. alcance vs. RRHH vs. hallazgo) y no duplicarlas entre secciones.
- **Cumplir literalmente lo que promete el título** de cada parte (ej. si dice "Backlog", tiene que haber backlog real).
- **Plan de fases ≠ backlog:** el backlog priorizado (épicas/historias) alimenta las fases y se refina por sprint.
- **Aclarar limitaciones donde se declara el alcance** (ej. dashboard = corte histórico con carga manual mensual, no datos en vivo).
- **Stakeholders:** distinguir influencia de diseño/técnica de influencia política/decisión.
