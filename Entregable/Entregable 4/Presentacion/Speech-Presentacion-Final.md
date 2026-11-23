# Speech · Presentación final (Grupo 1)

> Guion generado desde las notas del orador de `Casa-Oga-Presentacion-Final.pptx` (15 diapositivas, unos 15 minutos) por `armar_presentacion_final.js`. Para cambiarlo, editar el script y regenerar. Las cifras salen de `Modelo/resultados/modelo_final_v4_resultados.json` y `Dashboard/datos_dashboard.json`.

Tono: presentación de negocio a Casa Óga (Dirección, Compras, Finanzas y Operaciones), no exposición técnica. El detalle técnico y la sección «Cambios» están en el informe final.

| Orden | Quién | Diapositivas |
|---|---|---|
| 1 | Santiago · Comunicación | 1-3 |
| 2 | Gerónimo · Visualización | 4-7 |
| 3 | Matías · Datos | 8-9 |
| 4 | Simón · Modelado | 10-11 |
| 5 | Gianfranco · Coordinación | 12-14 |
| 6 | Santiago · Comunicación | 15 |

## 1 · Portada

SANTIAGO. Buenas, somos el Grupo 1. Venimos a presentarle a Casa Óga una herramienta concreta: una lista mensual, tienda por tienda, que dice qué stock se está quedando parado, qué hacer con él y por qué, antes de que aparezca en el conteo de fin de año. Les vamos a mostrar el problema en plata, el producto funcionando con los datos de agosto, lo que encontramos, cuánto cuesta y qué necesitamos de ustedes para arrancar. Matías trabajó los datos, Simón el modelo, Gerónimo el tablero y Gianfranco la economía y el plan.

## 2 · Hoy hay ARS 178,6 M parados en stock que no rota

SANTIAGO. Empecemos por el problema, en plata. En agosto hay 866 combinaciones de producto y tienda con más de un año de stock al ritmo de venta actual: son 178,6 millones de pesos a costo que no están trabajando. En diciembre eran 200. Entre 2023 y 2025 el problema era estable; en 2026, con la venta en baja, se cuadruplicó en ocho meses. Y hoy esto se ve recién en el conteo de fin de año, cuando ya pasaron meses de costo y liquidar sale más caro.

## 3 · Respondemos las tres preguntas de la Dirección

SANTIAGO. Cuando arrancamos, la Dirección nos hizo tres preguntas. Qué productos van a quedar parados en los próximos meses; qué distingue a los que rotan de los que no; y qué conviene liquidar o mover, y en qué tienda. Hoy tenemos una respuesta para cada una, y la van a ver funcionando. Les adelanto la propuesta: un piloto de tres cierres mensuales, con una inversión de 9.570 dólares, un tercio del presupuesto. Le paso a Gerónimo, que les muestra el producto.

## 4 · Una semana por mes, y siempre decide una persona

GERÓNIMO. Así funciona en el día a día. Con el cierre de cada mes recibimos las cinco exportaciones que Casa Óga ya genera; las ordenamos con las reglas que acordamos con ustedes; y armamos la lista: primero todo lo que ya tiene más de un año de stock, que se explica solo, y después las 150 posiciones que el modelo ve venir. Cada área recibe su vista. La tienda propone qué hacer, y Comercial y Compras autorizan en una reunión de media hora. Tres meses después medimos si acertamos y cuánto capital se liberó. No hace falta comprar nada: corre en una PC de oficina. Y una aclaración: el tablero es una foto mensual, no un sistema en vivo.

## 5 · Dirección: el mes en una pantalla

GERÓNIMO. Esta es la vista para la Dirección, con los datos reales de agosto. Arriba, lo que está en juego: 1.016 alertas por 189,1 millones de pesos. Al medio, mes a mes, cuántos casos detectó la lista contra la regla simple, en los meses que ya sabemos cómo terminaron. A la derecha, dónde está el problema: AMBA es la región con más alertas, cuatro de cada diez. Todo se filtra por región, tienda, categoría o proveedor.

## 6 · Tiendas: cada alerta llega con qué hacer y por qué

GERÓNIMO. Esta es la lista que recibe cada tienda. Está ordenada por capital, y cada tienda trabaja hasta 25 alertas por mes, el máximo que nos dijo Operaciones. Cada fila trae una acción sugerida: si otra tienda vende ese producto rápido, dice a cuál transferirlo; si no, liquidar. Y trae el motivo en palabras, por ejemplo: un año de cobertura y la venta del trimestre en cero. La versión para las tiendas se publica sin la columna de costos.

## 7 · Compras: qué no volver a comprar

GERÓNIMO. Para Compras la pregunta es otra: qué no volver a comprar. Acá ven el capital en alerta por categoría y por proveedor, que sirve para negociar devoluciones y condiciones. Y abajo, los productos que están en alerta en muchas tiendas a la vez: eso no se arregla moviendo mercadería, es una señal de que se compró de más. Finanzas y quien mantenga el modelo tienen sus propias vistas, que les dejamos en el tablero. Le paso a Matías con lo que encontramos.

## 8 · La primera lista: agosto de 2026

MATÍAS. Trabajamos con cuatro años de datos de las 28 tiendas, más de 200 mil registros mensuales de producto y tienda, limpiados con las reglas que acordamos con ustedes. Corrimos la lista de agosto y esto es lo que dice. Son 1.016 alertas por 189,1 millones. La buena noticia: 8 de cada 10 se resuelven transfiriendo, porque otra tienda vende ese producto rápido; no hace falta rematar. Segundo: 73 productos están parados en cinco tiendas o más y explican casi la mitad de las alertas; ahí el problema no es la ubicación, es cuánto se compró. Y tercero, Decoración y Textil hogar concentran 40% del capital.

## 9 · Hoy la lista no entra en las tiendas: hay que ponerse al día

MATÍAS. Y un hallazgo que no esperábamos. Sólo lo que ya pasó el año de stock son 866 posiciones, y las tiendas pueden trabajar 700 por mes: 25 cada una. En el gráfico, cada barra que pasa la línea punteada es una tienda desbordada. Como cada tienda empieza por las alertas de más plata, el 93% del capital entra igual en el cupo; el resto pasa al mes siguiente. Pero hay una decisión que es de la Dirección: hacer una limpieza puntual antes del piloto, o ponerse al día en dos o tres meses. Le paso a Simón, que cuenta por qué pueden confiar en la lista.

## 10 · Con las mismas alertas, encuentra más casos que la regla simple

SIMÓN. ¿Por qué confiar en la lista? La probamos con meses que ya sabemos cómo terminaron. Con la misma cantidad de alertas, nuestra lista detecta 404 casos en 2025 contra 354 de ordenar por cobertura: un 14% más. Marca entre el 51% y el 59% de lo que se iba a inmovilizar, tres meses antes. Y les somos honestos: en 2026 la ventaja es chica, 2%, porque con tanto stock parado la regla sola ya encuentra casi todo. Por eso proponemos un piloto que lo vuelva a medir antes de comprometer nada más.

## 11 · Mira lo que miraría un comprador, pero antes

SIMÓN. Y no es una caja negra. Medimos qué pasa si le escondemos al modelo cada dato: lo que más pesa es la venta de los últimos seis meses, la cobertura y lo irregular de la venta. Es lo mismo que miraría un comprador con experiencia, pero combinado y antes de que el producto cruce el año de stock. Cada alerta trae su motivo en palabras, y el modelo sólo ordena: nada se liquida ni se mueve sin que una persona lo decida. Le paso a Gianfranco con los números.

## 12 · Usa un tercio del presupuesto y se paga en dos años

GIANFRANCO. Vamos a los números. La inversión inicial es de 9.570 dólares, un tercio de los 30 mil del presupuesto, sin comprar infraestructura. En un año como 2025, el proyecto devuelve unos 10.849 dólares por año y cuesta 5.960 mantenerlo: el retorno a tres años es de 18,6% y la inversión se recupera en unos 24 meses. Fíjense de dónde sale el beneficio: la mayor parte viene de automatizar la lista y de las horas que hoy se van en armarla a mano; el modelo suma por encima. Elegimos 2025 como referencia a propósito: en un año como 2026 los números son mucho mejores, pero eso es un techo, no una promesa.

## 13 · Lo que puede salir mal, y cómo lo vemos a tiempo

GIANFRANCO. Tres cosas pueden salir mal, y para cada una definimos una señal que la detecta y una respuesta. Que el beneficio no alcance: si dos trimestres quedan por debajo de lo esperado, seguimos sólo con la lista automatizada, que se paga sola. Que los datos lleguen incompletos: esas filas no se publican hasta corregirlas. Y que el modelo no le gane a la regla: se apaga y se reentrena, sin costo extra. El supuesto que más mueve el número es el costo de desarrollo: si fueran tres meses de un especialista, el retorno a tres años queda apenas negativo, en -3,3%, y aun así está dentro del presupuesto. Del lado legal no hay datos personales, y las tiendas no ven costos.

## 14 · Preparación, piloto de tres cierres y decisión en el mes 6

GIANFRANCO. El plan es corto. Dos semanas para poner los datos al día con las correcciones que quedaron pendientes y repetir la evaluación; dos semanas más para nombrar al responsable, configurar los accesos y estandarizar la exportación. Después, un piloto de tres cierres mensuales. Como el resultado de una alerta se conoce tres meses después, entre los meses 4 y 6 medimos si la lista encontró más que la regla y cuánto capital liberó, y en el mes 6 Finanzas decide si sigue. De parte de Casa Óga hace falta poco: un responsable, la exportación mensual, media hora por mes de Comercial y Compras, y una PC que ya tienen. Le devuelvo la palabra a Santiago.

## 15 · Cierre

SANTIAGO. Cerramos. Casa Óga tiene hoy 178,6 millones de pesos parados y se entera en el conteo de fin de año. Les proponemos verlo todos los meses, tienda por tienda, con qué hacer y por qué. Para arrancar necesitamos tres decisiones: aprobar un piloto de tres cierres por 9.570 dólares; nombrar a un responsable; y elegir cómo ponerse al día con las 866 posiciones que hay hoy. El riesgo está acotado: si el modelo no suma, la lista automatizada igual se paga sola. Muchas gracias; quedamos para preguntas.
