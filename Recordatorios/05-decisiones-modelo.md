# Decisiones sobre el modelo — variable objetivo y semáforo

> **Estado: PROPUESTA, no aprobada.** Enviada a validación de María G. el [fecha]. Nada de esto es definición oficial de Casa Óga hasta que responda.
> Actualizado: 25-09-2026 (ventas negativas neteadas, ver al final) · Datos: `Datasets_Normalizados/` corte ago-2026 · Scripts: `Entregable/Entregable 2/EDA/candidatos_target.py`

## La propuesta en corto

| Pieza | Definición |
|---|---|
| **Variable objetivo** | Binaria: la posición SKU–tienda tiene cobertura > 12 meses dentro de 3 meses |
| **Unidad de análisis** | SKU–tienda–mes |
| **Universo** | Posiciones con `stock_disponible > 0` en el mes t, no discontinuadas, con **3+ meses de historia** |
| **Horizonte** | 3 meses (etiqueta en t+3, features hasta t) |
| **Cobertura** | `stock_disponible / promedio de unidades vendidas de los últimos 12 meses`, con las devoluciones neteadas |
| **Optimización** | Recall por encima de precisión |
| **Partición** | Temporal, nunca aleatoria |
| **Prevalencia** | 3,40% (6.853 positivos sobre 201.306 filas, dataset v3) |

**Semáforo:** Rojo > 12 meses · Amarillo 9 a 12 · Verde < 9.
**Acciones:** Rojo liquidar o transferir · Amarillo frenar reposición y vigilar · Verde nada.
**Discontinuados con stock:** afuera del modelo, lista aparte con regla fija (47% del capital inmovilizado).

---

## En qué se apoya cada decisión

| Decisión | Base | Solidez |
|---|---|---|
| Cobertura como métrica | El negocio pidió umbral relativo a la rotación de cada SKU, no absoluto (relevamiento TP1) | Firme |
| Horizonte 3 meses | Confirmado por el negocio: menos se confunde con estacionalidad; la acción tarda 2-4 semanas | Firme |
| Recall sobre precisión | El negocio declaró el falso negativo como más costoso | Firme |
| Corte en 12 meses | Capacidad operativa de 420-700 intervenciones/mes + coincide con rotación anual < 1, límite de "non-moving" del análisis FSN | Media |
| Sacar "sin ventas en 3 meses" | Medición propia (22% de probabilidad por azar) + los 90 días son umbral de FMCG, no de hogar y decoración | Media |
| **Corte en 9 meses** | **Solo el percentil 90 de nuestra distribución (9,3 meses)** | **Débil** |
| **Sacar discontinuados** | **Criterio propio: es una decisión ya tomada, no un evento a predecir** | **Débil** |
| **Acciones por banda** | **Nada. Asignación nuestra** | **Sin respaldo** |

> El corte de 12 meses salió **primero** de la capacidad operativa. La coincidencia con el FSN se encontró después, buscando fuentes. Sirve como respaldo, no fue el origen. No inventar un orden distinto al presentarlo.

---

## Por qué se descartaron los otros candidatos

> **Actualizado 28-09 (v3).** Con el universo ampliado a 3+ meses de historia (201.306 filas) la inercia ya no separa a los candidatos: la regla trivial acierta entre 33,5% y 38,6% en todos. La elección de D se sostiene por negocio (umbral relativo a la rotación, pedido de Comercial; sin discontinuados, que no existen en 2026; evento accionable), no por ser el menos inercial.
>
> | Candidato | Positivos | Info nueva | Recall regla trivial |
> |---|---|---|---|
> | A · Dead stock binario | 8,32% | 62% | 38,4% |
> | B · Cobertura > 12 o discontinuado | 3,99% | 67% | 33,5% |
> | C · Sin ventas en 3 meses | 6,18% | 65% | 35,3% |
> | **D · Cobertura > 12 sin discontinuados** | **3,40%** | **61%** | **38,6%** |
> | E · Cobertura > 9 | 9,93% | 62% | 38,5% |

Comparación original, sobre 131.189 filas con 12 meses de historia (se conserva como registro de cómo se eligió):

| Candidato | Positivos | Info nueva | Recall regla trivial | Veredicto |
|---|---|---|---|---|
| Dead stock binario (3 condiciones OR) | 8,51% | 58% | 41,8% | Descartado: mucha inercia |
| **Cobertura > 12 o discontinuado** | 3,85% | 71% | 28,6% | Mejor señal, pero ver problema de 2026 |
| Sin ventas en 3 meses | 6,75% | 58% | 42,2% | Descartado: el más inercial y el más ruidoso |
| **Cobertura > 12 sin discontinuados** | **3,38%** | **68%** | 32,5% | **Elegido** |
| Cobertura > 9 (rojo + amarillo) | 9,84% | 64% | 35,9% | Alternativa si hace falta volumen |

---

## Advertencias que NO hay que perder de vista

1. **La tasa objetivo no es estable:** entre 1,7% y 2,2% en 2023-2025 contra 9,0% en 2026 (con el criterio anterior, 1,1%-1,4% contra 8,3%; el "1,9%" que figuraba antes era la tasa del candidato B, no la del target elegido). La mediana de cobertura está clavada en 5,0 meses todo el período, pero el percentil 99 pasa de 15 a 48 meses entre enero y agosto de 2026: se engorda la cola justo en el tramo nuevo. No está explicado. Obliga a partición temporal y entra como pregunta al negocio.
2. **El catálogo está congelado desde junio 2025** (H12): en 2026 no hay ningún discontinuado. Si esa condición queda dentro del target, la etiqueta significa una cosa hasta dic-2025 y otra después. Es la razón técnica —además de la conceptual— para sacarla.
3. **Nuestros cortes son laxos contra el estándar del sector:** la práctica retail trata como stock muerto lo que pasa los 180 días. Con ese criterio la banda roja serían miles de posiciones. Nuestra defensa es la capacidad operativa, y hay que escribirla explícitamente en el entregable.
4. **Casa Óga rota 2,3 veces al año** contra un rango de 2,5 a 5,0 en home furnishings: está por debajo del piso de su industria.
5. **La capacidad de 15-25 intervenciones por tienda nunca se midió.** Todo el dimensionamiento depende de ese número.

---

## Pendiente de aprobación

**María G. (Comercial)** — es la aprobadora formal designada:
1. La definición de dead stock.
2. Los cortes de 12 y 9 meses.
3. La acción asignada a cada banda.
4. El ajuste por categoría, que pidió expresamente y quedó para la Fase 1. Dos temas abiertos ahí: "Regalos" no existe en el maestro, y la estacionalidad que percibe no aparece en los datos una vez descontado el crecimiento.

**Carlos F. (Financiera):** visto bueno sobre el criterio de stock y cobertura. Aparte, la base del 5% mensual (sobre costo da $4,2 M/mes, sobre lista $7,7 M/mes).

**Lucía O. (Operaciones):** confirmar las 15 a 25 intervenciones por tienda al mes.

**Sistemas y Compras:** las 32 preguntas de `Preguntas-Calidad-de-Datos-Ronda-2.docx`.

> Ojo al plantearlo: **le estamos pidiendo a María G. que cambie algo que ya había aprobado** (el semáforo por sell-through). El argumento es que su criterio marca 5.915 posiciones en rojo, el 74% del catálogo, contra una capacidad de 420-700. No es una preferencia técnica nuestra: no se puede ejecutar.

---

## Fuentes externas usadas

| Fuente | Qué respalda | Cercanía al rubro |
|---|---|---|
| Análisis FSN (rotación < 1 = non-moving) | El corte de 12 meses | Media (inventario general) |
| Benchmarks de rotación home furnishings (2,5-5,0 anual; 75-145 días) | Contexto de mercado y comparación con Casa Óga | **Alta** |
| Umbrales de antigüedad 90/180/365 días | Que los 90 días son criterio de FMCG, no de nuestro rubro | Media (blogs de proveedores) |
| Croston / Syntetos-Boylan, demanda intermitente | Que los períodos en cero son normales en baja rotación | Media (académico, citable) |
| IAS 2, valor neto realizable | Valuar a costo y la discusión de base del 5% | Baja en rubro, alta en autoridad |

**No existe una fuente académica que fije un umbral de cobertura para retail de hogar y decoración.** Cada retailer lo calibra. Decirlo así en el entregable en vez de aparentar que hay un estándar.

---

## Próximo paso

~~Mapa de features y script que construye el dataset de entrenamiento~~ **Hecho el 28-09-2026:** `Entregable/Entregable 2/Modelo/construir_dataset_modelo.py` → `Datasets_Modelo/dataset_entrenamiento_v3*` (201.306 filas × 60 features; v1 de 39 y v2 de 67 quedaron reemplazadas). Documentado en Parte B §2.1 y §2.2.

Decisiones tomadas al construirlo (revisar con el grupo):
- **Universo sin discontinuados en t** (además de excluirlos del target). `candidatos_target.py` usa el mismo universo desde v3.
- **v3 · historia mínima de 3 meses** (antes 12): con 12 quedaban afuera el 40% de las filas, el 45% de los positivos y todos los productos nuevos, que son los más riesgosos (6,8% de positivos en sus primeros 3 meses vs 3,4%). `historia_corta` marca las posiciones con menos de 12 meses. Las de menos de 3 meses necesitan una regla aparte.
- **v3 · fuera precio, costo y margen del catálogo** (y capital, venta en pesos y descuento implícito): el catálogo guarda solo el valor actual (P10), así que en meses pasados es anacrónico — el mismo argumento que excluye el estado del catálogo. Queda solo el precio relativo a la subcategoría.
- **v3 · fuera el stock en tránsito** (H6): sin definición y sin señal en 2026.
- **Partición con embargo de 3 meses:** train t dic-22→dic-24 · validación abr→sep-25 · test ene→may-26. Se pierden 27.775 filas para evaluar (ene-mar y oct-dic 2025); el modelo final se reentrena con todo.
- **Features descartadas:** antigüedad de tienda (H3), historial de precios (H8), devoluciones por motivo (H12, se apagarían en 2026), identificadores de tienda y SKU.
- `costo_imputado` queda como marca de control y no como feature (los 22 SKUs no aparecen en train).

Siguiente: modelado (línea base logística + árboles), elección de umbral en validación priorizando recall.

---

## Cambio de criterio · 25-09-2026 — ventas negativas neteadas

Las respuestas del negocio a la ronda 2 (P23) fijan como default **netear las devoluciones** contra la venta del mismo SKU-tienda-mes, en lugar de llevarlas a 0. `candidatos_target.py` pasa a usar ese criterio (variable `CRITERIO_NEG`; `clip` reproduce el anterior, log en `resultados/candidatos_target_log_clip.txt`).

| | Criterio anterior (a 0) | Criterio actual (neteo) |
|---|---:|---:|
| Positivos del target (universo 12 m) | 3.509 | **4.428** (+26%) |
| Positivos del target (universo v3, 3+ m) | 5.260 | **6.853** (+30%) |
| Prevalencia (12 m → v3) | 2,67% → 2,61% | **3,38% → 3,40%** |
| Información nueva | 71% | 68% |
| Recall de la regla trivial | 28,6% | 32,5% |

- Las devoluciones son ~1% de las unidades, pero el impacto se concentra en posiciones de **muy bajo volumen** (mediana 1 unidad/mes): una sola devolución baja el ritmo de 12 meses y empuja la cobertura por encima de 12. De las 2.442 posiciones-mes que cambian de clase, 339 quedan con venta neta ≤ 0 en 12 meses (cobertura infinita).
- **La elección del target no cambia:** D sigue teniendo mucha menos inercia que A y C (recall trivial 32,5% contra 41,8% y 42,2%).
- **Punto a discutir:** el motivo "sin rotación / no vendido" (~21% de las unidades devueltas) es devolución **al proveedor** (P18), que el negocio reconoce como un movimiento de inventario y no como venta (P19). Netearlo baja el ritmo de venta de posiciones que no perdieron demanda. Si se decide excluir ese motivo del neteo hay que justificarlo, porque se aparta del default.

---

## Evidencia de que el dataset tiene señal · 28-09-2026

Medido con un modelo **de prueba** (gradient boosting sin ajustar, entrenado solo en train). No es el modelo final; sirve para saber que vale la pena modelar. Resultados en `Entregable/Entregable 2/Modelo/resultados/`.

| Prueba | Resultado | Lectura |
|---|---|---|
| Casos capturados con 420 alertas/mes (validación) | **58%** modelo vs **47%** regla «ordenar por cobertura actual» | +25% de casos con la misma capacidad |
| Con 700 alertas/mes | 73% vs 57% | Con menos de ~100 alertas la regla es igual o mejor |
| Casos que hoy NO están en rojo | **55%** de los positivos | Un semáforo sobre el presente no los ve: justifica anticipar |
| Mapa cobertura × tendencia | 9-12 meses de cobertura: 4,0% si la venta está estable, 9,4% si cae > 50% | La tendencia multiplica el riesgo; ninguna regla de un umbral lo captura |
| Señal por variable | 30 de 55 numéricas con AUC < 0,55 solas; top 15 = demanda y stock de la posición | Las acciones comerciales pasadas no separan solas |
| Stock en tránsito | AUC 0,67 en train → 0,50 en test (v2) | Pierde la señal en 2026 (H6): **sacado en v3** |
| v1 (39) vs v2 (67) vs v3 (60) | Misma performance (AUC ~0,90 validación, ~0,97 test) | La selección final se hace en el modelado |

**Advertencias nuevas:**
- **2026 no tiene devoluciones registradas** (H12): el neteo solo afecta 2022-2025. Las ventanas de 12 meses de principios de 2026 todavía incluyen devoluciones de 2025. No explica el salto de prevalencia (iría en sentido contrario), pero hay que declararlo.
- La capacidad de 420-700 intervenciones/mes **decide el umbral** del modelo y nunca se midió: validarla con Lucía O. antes del Entregable 3.

