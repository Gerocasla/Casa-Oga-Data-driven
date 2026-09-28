# Checklist Unidad 2 — qué pide cada clase y dónde está resuelto

> Diapositivas en `Material/Unidad 2/`. Revisado el 28-09-2026 contra el Entregable 2 (Partes A y B).
> ✅ resuelto · ⚠️ resuelto con salvedad · ❌ falta

## Clase 6 · EDA y calidad de datos → Entregable 2 · Parte A (y Parte B §1.1)

| Pide | Estado | Dónde |
|---|---|---|
| EDA: forma de los datos, relaciones, anomalías | ✅ | Parte A §2.3 (24 filas) + anexo con 12 gráficos, corte ago-2026 |
| Análisis univariado, bivariado y multivariado | ⚠️ | Parte A §2.3. Revisar que haya al menos un cruce multivariado explícito (p. ej. cobertura × categoría × región) |
| 7 dimensiones: completitud, exactitud, unicidad, validez, consistencia, actualidad, trazabilidad | ✅ | Parte A §3.1 y mapa actualizado en Parte B §1.1 |
| Distinguir consistencia de completitud (no proponer la acción equivocada) | ✅ | Cada hallazgo H1-H12 tiene una sola dimensión principal |
| Mapa de calidad fuente × dimensión | ✅ | Parte B §1.1 (15 fuentes × 7 dimensiones) |

## Clase 8 · Preparación de datos → Entregable 2 · Parte B §2

| Pide | Estado | Dónde |
|---|---|---|
| Relevancia de cada fuente (alta/media/baja) según cuánto aporta al target | ✅ | Parte B §2.1, tabla "Criterios de selección de fuentes" |
| C1 relevancia · C2 historia 12-18 meses · C3 calidad · C4 privacidad · C5 accionabilidad · C6 sesgo | ✅ | Misma tabla + párrafo "Riesgos de sesgo" |
| Granularidad correcta (agregar al grano del modelo) | ✅ | SKU-tienda-mes; eventos agregados por ventana |
| Target validado con el negocio antes de etiquetar | ⚠️ | Definido y calculado, **pendiente de aprobación de María G.** Cambiar la definición cambia la distribución de clases (la cátedra lo remarca) |
| Contexto temporal / estacionalidad | ⚠️ | Mes del año (seno/coseno). Calendario no se usa porque no cubre 2026 (H12); justificado |
| Integración de costos (¿el costo está actualizado para todo el período?) | ✅ | Costo de catálogo + supuesto 1,2321 para 22 SKUs, marcado con `costo_imputado` |
| Nulos, tipos, outliers (validar con negocio antes de eliminar), encoding, **data leakage** | ✅ | Parte B §2.2 (8 filas, incluida "prevención de leakage") |
| Gobernanza y Ley 25.326 | ✅ | Ninguna de las 15 fuentes tiene datos personales (dicho en §2.1). Faltas de gobierno (sin data owner, sin diccionario, sin retención) están en los gaps de §1.1 |

## Clase 7 · Errores frecuentes del TP1 → consolidado final

La cátedra dice que **para la presentación final estas 10 preguntas tienen que estar resueltas**. Estado de nuestro TP1 (detalle en `02-correcciones-tp1.md`):

| # | Pregunta del checklist | Estado | Corrección |
|---|---|---|---|
| 1 | ¿El contexto de mercado cita al menos una fuente externa que sostenga la afirmación del Problem Statement? | ❌ | #5 |
| 2 | ¿La Visión promete solo la anticipación que el mecanismo sostiene? | ❌ | #10 (nueva) |
| 3 | ¿Cada objetivo específico tiene un mínimo aceptable? | ❌ | #11 (nueva) |
| 4 | ¿El Alcance deja explícito qué es prototipo, qué está congelado y qué queda fuera? | ❌ | #9 |
| 5 | ¿El Problem Statement va de afuera hacia adentro y cuantifica la urgencia? | ❌ | #1, #2 |
| 6 | ¿El mapa de stakeholders incluye a todo actor que condiciona la parte técnica? | ❌ | #6, #12 (nueva) |
| 7 | ¿Cada restricción está en su categoría, sin duplicarse? | ❌ | #7, #8 |
| 8 | ¿Todas las cifras que se repiten coinciden? | ❌ | #1, D1-D13, 431/620/661 |
| 9 | ¿Existe un Backlog inicial real, separado del cronograma? | ❌ | #3 |
| 10 | ¿Todo archivo que el texto dice "se adjunta" está en la entrega? | ❌ | #13 (nueva) |

## Qué quedó hecho el 28-09-2026

- Parte B §1.3: dashboard antes/después (`Entregable 2/Dashboard-Calidad-Antes-Despues.html`, script `EDA/antes_despues.py`, figura `EDA/graficos/13_antes_despues.png`) y tabla con 11 métricas.
- Parte B §2.1 y §2.2 completas. Dataset `Datasets_Modelo/dataset_entrenamiento_v3*` (60 features, universo 3+ meses) generado por `Entregable 2/Modelo/construir_dataset_modelo.py`, con tabla de variables excluidas.
- Parte A recalculada al corte ago-2026. Dashboard de 5 pestañas. Presentación en un solo archivo: v1 completa (34) y v2 corta (14), HTML y PDF, en `Entregable 2/Presentacion/`.
- Respuestas de la ronda 2 archivadas en `Material/Respuestas-Ronda-2-Calidad-de-Datos.md`, con la tabla de dónde se aplicó cada una.
