# Decisiones sobre el modelo — variable objetivo y semáforo

> **Estado: PROPUESTA, no aprobada.** Enviada a validación de María G. el [fecha]. Nada de esto es definición oficial de Casa Óga hasta que responda.
> Actualizado: 23-09-2026 · Datos: `Datasets_Normalizados/` corte ago-2026 · Scripts: `Entregable/Entregable 2/EDA/candidatos_target.py`

## La propuesta en corto

| Pieza | Definición |
|---|---|
| **Variable objetivo** | Binaria: la posición SKU–tienda tiene cobertura > 12 meses dentro de 3 meses |
| **Unidad de análisis** | SKU–tienda–mes |
| **Universo** | Posiciones con `stock_disponible > 0` en el mes t |
| **Horizonte** | 3 meses (etiqueta en t+3, features hasta t) |
| **Cobertura** | `stock_disponible / promedio de unidades vendidas de los últimos 12 meses` |
| **Optimización** | Recall por encima de precisión |
| **Partición** | Temporal, nunca aleatoria |
| **Prevalencia** | 2,67% (3.509 positivos sobre 131.189 filas) |

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

Comparación sobre 131.189 filas, etiqueta a 3 meses. La columna que decide es el recall de la regla trivial "va a seguir igual que hoy": si es alto, el target es pura inercia y el modelo no aporta.

| Candidato | Positivos | Info nueva | Recall regla trivial | Veredicto |
|---|---|---|---|---|
| Dead stock binario (3 condiciones OR) | 7,41% | 58% | 41,8% | Descartado: mucha inercia |
| **Cobertura > 12 o discontinuado** | 3,15% | 76% | 24,4% | Mejor señal, pero ver problema de 2026 |
| Sin ventas en 3 meses | 6,04% | 56% | 44,3% | Descartado: el más inercial y el más ruidoso |
| **Cobertura > 12 sin discontinuados** | **2,67%** | **71%** | 28,6% | **Elegido** |
| Cobertura > 9 (rojo + amarillo) | 8,52% | 68% | 32,3% | Alternativa si hace falta volumen |

---

## Advertencias que NO hay que perder de vista

1. **La tasa objetivo no es estable:** 1,9% en 2023-2025 contra 8,3% en 2026. La mediana de cobertura está clavada en 5,0 meses todo el período, pero el percentil 99 pasa de 15 a 48 meses entre enero y agosto de 2026: se engorda la cola justo en el tramo nuevo. No está explicado. Obliga a partición temporal y entra como pregunta al negocio.
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

Mapa de features y script que construye el dataset de entrenamiento (tabla 2.1 y 2.2 del Entregable 2 · Parte B). Ver limitaciones vigentes en `PROBLEMAS-CALIDAD-DATOS.md`: H1 duplicados, H3 ventas antes de apertura, H8 precios, H12 fuentes sin 2026.
