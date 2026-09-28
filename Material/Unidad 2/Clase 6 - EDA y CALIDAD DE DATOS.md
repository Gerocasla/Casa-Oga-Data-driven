# Clase 6 - EDA y CALIDAD DE DATOS

> Materia: Factibilidad de Proyectos Data Driven · Unidad 2.
> Fuente: `Clase 6 - EDA y CALIDAD DE DATOS.pdf`. Se conserva la numeración de las diapositivas.

## Diapositiva 2

¿Dónde entra esto en CRISP-DM?

> La diapositiva contiene un esquema visual; consultar el PDF para ver su disposición.

## Diapositiva 3

¿Qué es EDA?

Análisis Exploratorio de Datos (EDA): proceso de examinar un dataset para entender su estructura, detectar patrones, identificar

anomalías y formular hipótesis, antes de aplicar cualquier técnica de modelado.

Tres preguntas que EDA responde

• ¿Qué forma tienen mis datos? (tipos de variable, rangos, distribuciones)

• ¿Qué relaciones hay entre variables? (correlaciones, dependencias)

• ¿Qué está mal o es sospechoso? (faltantes, outliers, inconsistencias)

Ejemplo Casa Óga, Proyecto Predecir Rentabilidad en Tiendas: antes de construir el modelo un EDA rápido sobre las

ventas muestra que una tienda tiene unidades vendidas en cero durante varias semanas seguidas.

¿Es una tienda cerrada por remodelación, un error de carga, o un problema real de reposición?

EDA no responde, hace visible la pregunta antes de que contamine el modelo.

## Diapositiva 4

Tipos de Análisis: Univariado, bivariado, multivariado

Ejemplo Casa Óga, Proyecto Rentabilidad en Tiendas:

• Univariado: distribución del margen bruto % por tienda-mes.

• Bivariado: margen real vs. margen presupuestado, para ver qué tan seguido y por cuánto se desvían las tiendas.

• Multivariado: margen + nivel de descuento aplicado + región, todo junto, para ver si el efecto de las promociones

sobre el margen varía según dónde está la tienda.

## Diapositiva 5

Lo que no puede faltar

> La diapositiva contiene elementos visuales sin texto extraíble; consultar el PDF.

## Diapositiva 6

Dimensiones de calidad de datos

Ejemplo Casa Óga: el identificador de tienda no siempre se registra con el mismo formato en todas las fuentes

(ventas, presupuesto, stock, maestro de tiendas). Si no se detecta esto antes de cruzar tablas, el join arma mal la

tienda-mes y el modelo termina prediciendo margen para combinaciones que no existen realmente.

Es un problema de consistencia, no de completitud, confundir estas dos dimensiones lleva a proponer la acción de

mejora equivocada.

## Diapositiva 7

COMPLETITUD

¿Faltan valores o registros que deberían estar?

Definición

Proporción de registros que tienen valor en cada campo

obligatorio. Un campo nulo o vacío donde debería haber

dato es un problema de completitud.

¿Qué preguntas debemos hacernos?

• ¿Cuántos nulos tiene cada columna?

• ¿Se concentran en alguna tienda o período?

• ¿El nulo significa 'no hay dato' o 'valor = 0'?

## Diapositiva 8

EXACTITUD

¿El valor registrado refleja la realidad?

Definición

Un dato es exacto cuando refleja correctamente el objeto

o evento del mundo real que representa. No basta con

que sea válido — debe ser verdadero.

¿Qué preguntas hacernos?

• ¿Los cálculos derivados son consistentes con sus

componentes?

• ¿Hay ventas de productos que no existen en el maestro?

• ¿Hay fechas fuera del período declarado?

## Diapositiva 9

UNICIDAD

¿Hay registros duplicados que no deberían existir?

Definición

Cada hecho real debe estar registrado exactamente una

vez. Un duplicado es cuando el mismo evento aparece dos

o más veces en el dataset.

¿Qué preguntas hacernos?

• ¿El duplicado es igual en todos los campos (copia exacta)?

• ¿O difiere en algún valor (ej: dos montos para el mismo mes)?

• ¿Cuál de los dos registros es el correcto?

## Diapositiva 10

VALIDEZ

¿El valor respeta el formato o rango esperado (tipo de dato, dominio)?

Definición

Un dato es válido cuando pertenece al conjunto de valores

aceptables para ese campo: rangos numéricos correctos,

formatos de fecha, catálogos cerrados, tipos de dato

consistentes.

¿Qué preguntas hacernos?

• ¿Los valores numéricos están dentro del rango esperado?

• ¿Los campos categóricos usan un catálogo cerrado?

• ¿Los tipos de dato son correctos (fecha como fecha, no string)?

## Diapositiva 11

CONSISTENCIA

¿El mismo dato se representa igual en todas las fuentes/tablas?

Códigos de tienda

Categorías de producto

Categorías de producto — caso vs. maestro

Caso de negocio Productos.csv

Archivo Formato

Stock 2022-2023 SXXX

Ventas / Presupuesto TXX

Presupuesto 2024-25 Texto Libre

Tiendas TXX

Misma tienda Distinta denominación

Textil hogar Hogar

• ¿Cuántos nulos tiene cada columna?

Cocina y mesa Cocina

• ¿Se concentran en alguna tienda o período?

Organización Baño

• ¿El nulo significa 'no hay dato' o 'valor = 0'?

Decoración Decoración ✓

Solo 'Decoración' coincide.

## Diapositiva 12

ACTUALIDAD

¿La información está disponible a tiempo para la decisión que debe soportar?

Definición

La actualidad (o vigencia) mide si el dato está disponible

cuando se necesita y si sigue siendo representativo de la

realidad actual. Un dato puede ser exacto en el momento en

que fue cargado, pero haber quedado desactualizado.

¿Qué preguntas hacernos?

• ¿El maestro refleja los precios actuales de venta?

• ¿El calendario de eventos está al día?

• ¿Los costos unitarios reflejan el momento de la venta

o el precio de compra original?

## Diapositiva 13

Mapa de Calidad: ¿dónde están los problemas?

Dataset Completitud Unicidad Validez Exactitud Consistencia Actualidad Trazabilidad

Ventas 22-23 146 nulos ✗20 dups 73 precios 71 filas ✓T01-T15 fechas 2021 ✗promo_id

Ventas 24-25 7 promo_id ✓ ✓ ✓ ✓T01-T15 ✓ ✗promo_id

Stock 22-23 ✓ ✓ ✓ ✓ ✗S001/T01 Mensual snapshot

Stock 24-25 175 nulos ✓ ✓ ✓ ✓T01-T15 ✗Diario→mes nulo≠0

Presupuesto ✓ ✗TIENDA_03 ✓ ✓ ✗TIENDA_03 ✓ ✓

Productos ✓ ✓ ✓ ✓ ✗Categorías ✗precio_base P9999

Promociones cuotas ✓ ✓ ✓ ✓4 tipos ✓ ✗sin linkeo

✓Sin problemas Issue menor ✗Issue crítico
