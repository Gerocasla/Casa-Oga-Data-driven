# Clase 8 - Preparacion de Datos

> Materia: Factibilidad de Proyectos Data Driven · Unidad 2.
> Fuente: `Clase 8 - Preparacion de Datos.pdf`. Se conserva la numeración de las diapositivas.

## Diapositiva 2

FUENTES DISPONIBLES EN EL CASO: ESTOS EJEMPLOS CORRESPONDEN A LOS CASOS EJEMPLO

PROYECTO RELEVANCIA ¿QUÉ CONTIENE? ARCHIVO

Ambos Alta Ticket, tienda, producto, descuento, venta neta Ventas_2024_2025_V2.csv

Ambos Alta Mismo esquema, período anterior Ventas_2022_2023_V2.csv

Ambos Alta Costo unitario + margen bruto de referencia Costos_Productos.csv

Tiendas Media Ventas presupuestadas por tienda/mes — no contiene margen Presupuesto_2024_2025.csv

Promos Alta Tipo, descuento, fechas, producto Promociones_2022–2025 (varios)

Tiendas Media Stock disponible por tienda/producto/fecha Stock_2024_2025.csv

Tiendas Media Región y tipo de tienda tiendas.csv

Tiendas Baja Fecha, tienda, canal (físico/online) — volumen implícito en ventas tickets.csv

Promos (online) Alta Ventas online con DNI, nombre Ventas_Ecommerce_2024_202 5.csv

Ambos Media Fechas de eventos comerciales calendario.xlsx

## Diapositiva 3

CUAL ES LA DISTINCIÓN DE RELEVANCIA

La distinción tiene que ver con qué tan directamente contribuye cada fuente a construir la variable objetivo del modelo.

Las fuentes de relevancia alta son las que contienen o permiten calcular directamente las variables centrales:

• Ventas: sin esto no hay variable objetivo ni características de comportamiento

• Costos: sin esto no se puede calcular margen, que es el corazón de ambos modelos

• Promociones: son la variable de intervención que queremos evaluar en el modelo de promos

Las fuentes de relevancia media aportan contexto que enriquece el modelo pero no lo define:

• Stock: útil para explicar quiebres o sobrestock como factor de margen, pero el modelo puede funcionar sin él

• tiendas.csv: región y tipo son variables de segmentación, no de comportamiento directo

• tickets.csv: permite calcular frecuencia de visitas o volumen de transacciones, pero ese dato está implícito en ventas

• Calendario: mejora la captura de estacionalidad

La clasificación no es rígida depende de cómo se defina la variable objetivo. Si por ejemplo se decide que la definición de

"margen bajo" incorpora días de inventario, entonces Stock sube a relevancia alta. Si se quiere modelar conversión por tienda,

tickets.csv se vuelve central.

## Diapositiva 4

CRITERIOS DE SELECCIÓN: ¿CÓMO DECIDIMOS?

Criterio 1: Relevancia para el objetivo

Criterio 3: Calidad y completitud

¿Este dato ayuda a predecir margen bajo o

Archivos con muchos nulos o inconsistencias en

efectividad de promo? Si no tiene relación causal

campos clave (producto, tienda, fecha) generan

clara con la variable objetivo, no lo incluimos todavía.

Criterio 2: Disponibilidad histórica suficiente

Necesitamos al menos 12–18 meses para

capturar estacionalidad. Datos muy escasos o

con gaps grandes pueden deteriorar el modelo.

ruido. Evaluamos antes de incluir.

Criterio 4: Riesgo legal/privacidad

Datos con información personal identificable

(DNI, nombre) requieren tratamiento especial o

anonimización antes de usarlos en el modelo.

## Diapositiva 5

Criterio 5 • Accionabilidad

¿Puede algún stakeholder tomar una decisión diferente si este dato aparece como predictor relevante?

Si la respuesta es no, la variable puede ser contexto pero no el foco del modelo.

Ej. 1 Región de la tienda: si el modelo detecta que las tiendas del NOA tienen margen más bajo, pero

Casa Óga no puede reubicarlas, esa variable describe pero no habilita acción. En cambio, "% de ventas

con descuento en los últimos 3 meses" para esa tienda sí es accionable: MG puede ajustar la política

promocional.

Ej. 2 Tipo de tienda (shopping / calle / outlet): el tipo en sí no es modificable. Lo accionable es lo que

explica su comportamiento: ticket promedio, mix de categorías, frecuencia de promociones aplicadas.

Sobre esas variables sí se puede intervenir.

## Diapositiva 6

Criterio 6 • Riesgo de sesgo

El historial de Casa Óga refleja decisiones humanas pasadas. El modelo aprende esos patrones y puede

perpetuarlos.

Sesgo promocional: si ciertas tiendas siempre recibieron más soporte promocional, el modelo puede

subestimar el potencial de las que nunca fueron expuestas a ese soporte.

Sesgo de precio: si ciertos productos siempre tuvieron descuento alto, el modelo puede concluir que

"necesitan descuento para vender" cuando simplemente nunca se probó a precio lleno.

Sesgo operativo: si el stock de algunas tiendas estuvo mal gestionado durante meses, los datos de

rotación de esas tiendas reflejan un problema operativo, no demanda real.

## Diapositiva 7

CRITERIOS FUNCIONALES: LO QUE EL NEGOCIO NECESITA

Convierten registros operativos en insumos útiles para un modelo predictivo.

GRANULARIDAD CORRECTA TIENDA X MES

El modelo de tiendas trabaja a nivel tienda–mes. Los datos de ventas están a nivel transacción diaria →

hay que agregar. Campos a calcular: venta_neta total, unidades totales, margen estimado, % ventas con

promo, % desvío vs presupuesto.

VARIABLE OBJETIVO: DEFINICION DE MARGEN BAJO

El caso plantea dos opciones: (a) margen bruto % menor al presupuestado, o (b) por debajo de un umbral fijo

(ej. 25%). Esta definición debe validarse con el negocio antes de etiquetar los datos. Cambiar la definición

cambia la distribución de clases.

CONTEXTO TEMPORAL: ESTACIONALIDAD Y EVENTOS

El negocio tiene picos fuertes (Hot Sale, CyberMonday, temporada verano/invierno). El calendario debe

integrarse como variable: mes, semana de evento, días desde último evento. Sin esto, el modelo no aprende la

estacionalidad.

## Diapositiva 8

CRITERIOS FUNCIONALES: LO QUE EL NEGOCIO NECESITA

UNIFICACION DE FUENTES DE PROMOCIONES

Hay al menos 6 archivos de promociones (2022–2025, histórico recuperado, online). Antes de usar, hay que:

unificar esquemas, verificar IDs consistentes, cruzar con ventas para saber si la promo efectivamente se aplicó

en cada tienda.

INTEGRACION DE COSTOS AL MODELO DE MARGEN

Ventas_2024_2025_V2 tiene precio_lista, descuento_pct y precio_neto_unit pero no costo. Hay que

cruzar con Costos_Productos por el campo "producto" para calcular margen unitario real. Atención: ¿el

costo está actualizado para todo el período?

## Diapositiva 9

CRITERIOS TÉCNICOS: LO QUE EL MODELO NECESITA

Valores nulos y faltantes

El EDA ya identificó problemas. Estrategia: imputar con mediana por categoría, o eliminar filas si el campo es clave (fecha,

tienda, producto).

Tipos de datos consistentes

Fechas como string en varios archivos > parsear a datetime. Precios como float, IDs como string (no mezclar T11 con t11).

Outliers

Ventas anómalas pueden ser errores de carga o eventos reales. Validar con el negocio antes de eliminar.

Codificación de variables categóricas

Tienda, región, tipo_tienda, categoría > encoding. Cuidado con label encoding ordinal en variables nominales.

Data leakage

No incluir variables que solo se conocen después del período que queremos predecir (ej: venta real del mes siguiente al

entrenar).

## Diapositiva 10

Gobernanza y aspectos legales

El caso menciona explícitamente que Casa Óga no tiene políticas formales de datos ni una revisión legal asociada al proyecto.

Esto es un riesgo real que el equipo analítico debe gestionar.

Ley 25.326 — Protección de Datos Personales (Argentina) Es la norma principal que aplica al caso. Establece que los datos personales (DNI, nombre, datos de consumo asociados a personas) solo pueden usarse con el consentimiento del titular o cuando existe una base legal legítima. El uso de datos de clientes en un modelo predictivo sin política documentada puede constituir una infracción.

PRINCIPIOS A APLICAR

Minimización: solo recolectar y usar los datos estrictamente necesarios para el objetivo del modelo.

Proporcionalidad: el uso analítico debe ser proporcional al objetivo declarado.

Finalidad: los datos capturados para ventas no fueron recogidos con el fin explícito de usarse en un modelo predictivo

> posible brecha.

## Diapositiva 11

Gobernanza y aspectos legales

DATOS PERSONALES EN EL CASO

Identifican directamente a una persona física. Para usar en analytics:

(a) anonimizar irreversiblemente, o

(b) seudonimizar con hash y guardar la tabla de correspondencia con acceso restringido. El modelo no

necesita saber el nombre del cliente.

TRANSACCIONES CON ID_TICKET

Por sí solo no identifica a una persona, pero combinado con fecha, tienda y canal puede ser re-identificable.

Riesgo bajo en el contexto del modelo, pero debe evaluarse.

## Diapositiva 12

Gobernanza y aspectos legales

SITUACIÓN ACTUAL

LO QUE DEBERÍA EXISTIR

►Sin clasificación de datos

►Accesos no documentados

►Sin responsable de datos

►Sin política de retención

►Sin revisión legal previa

►Inventario y clasificación de datos

►Roles y permisos definidos

►Data owner por dominio

►Política de retención documentada

►Revisión legal antes del proyecto

## Diapositiva 13

Gobernanza y aspectos legales

Caso crítico: Ventas_Ecommerce_2024_2025.csv contiene DNI y

nombre completo.

Este archivo no puede usarse directamente en el modelo sin antes

anonimizar o seudonimizar esos campos.

## Diapositiva 14

RECOMENDACIONES MÍNIMAS PARA EL PROYECTO RESPECTO A GOBERNANZA

Inventario de datos personales

Identificar qué archivos contienen datos personales, quién los usa y con qué finalidad. Esto es el primer paso

antes de cualquier proyecto analítico.

Anonimizar o seudonimizar antes de modelar

El DNI y nombre del ecommerce deben quitarse del dataset de entrenamiento. Si se necesita trackear

comportamiento individual, usar un ID interno hasheado.

Control de acceso al proyecto

Definir quién puede ver los datos crudos (equipo técnico reducido) vs. quién solo accede a resultados del

modelo (dirección comercial, finanzas).

Documentar la base legal del uso

Registrar el propósito del procesamiento, la base legal invocada y las medidas de protección aplicadas. Esto

protege a la empresa ante un eventual reclamo.
