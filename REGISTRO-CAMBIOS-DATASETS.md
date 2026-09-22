# Registro de cambios sobre los datasets — Casa Óga

Bitácora de **todo** lo que se toca en los datos. Orden cronológico, lo más nuevo al final.

**Convención de carpetas:**
- `Datasets/` → los CSV tal como los entrega la cátedra. **No se editan nunca.** Si llega una versión nueva, la anterior se guarda en `Datasets/_originales_reemplazados/` con la fecha.
- `Datasets_Normalizados/` → mismos datos, con la representación unificada. **Es la carpeta que deben usar los análisis.**
- Toda transformación se hace con un script versionado, nunca a mano.

---

### 22-09-2026 — Llegan versiones actualizadas de 3 datasets (desde el repo)

Origen: repositorio GitHub del grupo, commits `94b7918`, `f1c7b76`, `8ada276` y `81a3e4f`. Los archivos venían nombrados `Liquidaciones (1).csv`, `Stock_SKU_tienda_mensual (2).csv` y `Ventas_SKU_tienda_mensual (1).csv`; se renombraron al nombre estándar.

| Dataset | Antes | Ahora | Qué cambió |
|---|---|---|---|
| Ventas_SKU_tienda_mensual | 239.336 filas, ene-22 a dic-25 | **299.400 filas, ene-22 a ago-26** | +60.064 filas nuevas (8 meses más). Las claves viejas siguen todas presentes. |
| Stock_SKU_tienda_mensual | 239.336 filas, ene-22 a dic-25 | **299.400 filas, ene-22 a ago-26** | +60.064 filas nuevas. Idem. |
| Liquidaciones | 508 registros | **593 registros** | +85 registros. Los 508 anteriores quedaron idénticos. |

Las versiones anteriores quedaron en `Datasets/_originales_reemplazados/*.2026-09-15`.

**Efectos a tener en cuenta:**
- El corte de los datos pasa de dic-2025 a **ago-2026**, alineado con Presupuesto, Stock depósito, Órdenes de compra, Transferencias, Precios y Promociones, que ya llegaban a 2026. Queda pendiente decidir el corte de análisis.
- **Los problemas de calidad conocidos siguen igual:** 2.378 duplicados por clave en cada archivo, 1.209 stocks negativos, 2.317 ventas negativas, 3 descuentos fuera de rango. No se corrigió ninguno en esta actualización.
- Todos los números del TP1 y del EDA previo están calculados sobre el corte a dic-2025 y hay que recalcularlos.

---

### 22-09-2026 — Normalización de representación (R1 a R4)

Generado por `Entregable/Entregable 2/EDA/normalizar_datasets.py`. Origen: `Datasets/` (sin tocar) → salida: `Datasets_Normalizados/`.

**Total: 2,712 celdas normalizadas.** Filas, columnas, nulos y valores numéricos sin cambios (verificado).

| Fuente | Columna | Regla | Valor crudo | Valor normalizado | Filas |
|---|---|---|---|---|---|
| Calendario | temporada | R1 sin tildes/enie | `Otoño` | `Otono` | 368 |
| Costo_almacenamiento | categoria | R2 categoria unificada | `Baño` | `Bano` | 1 |
| Devoluciones_SKU | motivo | R1 sin tildes/enie | `Producto dañado en logistica` | `Producto danado en logistica` | 499 |
| Liquidaciones | fecha_fin | R3 formato de fecha | `2023-02-04 00:00:00` | `2023-02-04` | 1 |
| Liquidaciones | fecha_fin | R3 formato de fecha | `2023-12-24 00:00:00` | `2023-12-24` | 1 |
| Liquidaciones | fecha_fin | R3 formato de fecha | `2024-02-24 00:00:00` | `2024-02-24` | 1 |
| Liquidaciones | fecha_fin | R3 formato de fecha | `2024-07-28 00:00:00` | `2024-07-28` | 1 |
| Liquidaciones | fecha_fin | R3 formato de fecha | `2024-09-03 00:00:00` | `2024-09-03` | 1 |
| Liquidaciones | fecha_fin | R3 formato de fecha | `2025-10-08 00:00:00` | `2025-10-08` | 1 |
| Liquidaciones | fecha_fin | R3 formato de fecha | `2026-01-22 00:00:00` | `2026-01-22` | 1 |
| Liquidaciones | fecha_fin | R3 formato de fecha | `2026-02-23 00:00:00` | `2026-02-23` | 1 |
| Presupuesto_Ventas_Tienda_Categoria | categoria | R2 categoria unificada | `Baño` | `Bano` | 1,568 |
| Productos_catalogo | categoria | R2 categoria unificada | `Baño` | `Bano` | 100 |
| Productos_catalogo | categoria | R2 categoria unificada | `Decoración` | `Decoracion` | 8 |
| Productos_catalogo | categoria | R2 categoria unificada | `Textil Hogar` | `Textil hogar` | 6 |
| Productos_catalogo | categoria | R2 categoria unificada | `DECO` | `Decoracion` | 5 |
| Productos_catalogo | categoria | R2 categoria unificada | `TEXTIL_HOGAR` | `Textil hogar` | 2 |
| Productos_catalogo | subcategoria | R1 sin tildes/enie | `Alfombras de baño` | `Alfombras de bano` | 40 |
| Productos_catalogo | subcategoria | R1 sin tildes/enie | `Accesorios de baño` | `Accesorios de bano` | 30 |
| Productos_catalogo | subcategoria | R1 sin tildes/enie | `Cortinas de baño` | `Cortinas de bano` | 30 |
| Promociones_Comerciales | categoria | R2 categoria unificada | `Baño` | `Bano` | 16 |
| Promociones_Comerciales | categoria | R2 categoria unificada | `Decoración` | `Decoracion` | 1 |
| Promociones_Comerciales | categoria | R2 categoria unificada | `TEXTIL_HOGAR` | `Textil hogar` | 1 |
| Promociones_Comerciales | categoria | R2 categoria unificada | `Textil Hogar` | `Textil hogar` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Buenos Aires 10` | `Casa Oga Buenos Aires 10` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Buenos Aires 2` | `Casa Oga Buenos Aires 2` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Buenos Aires 20` | `Casa Oga Buenos Aires 20` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Buenos Aires 23` | `Casa Oga Buenos Aires 23` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Buenos Aires 24` | `Casa Oga Buenos Aires 24` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Buenos Aires 27` | `Casa Oga Buenos Aires 27` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Buenos Aires 5` | `Casa Oga Buenos Aires 5` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga CABA 11` | `Casa Oga CABA 11` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga CABA 14` | `Casa Oga CABA 14` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga CABA 22` | `Casa Oga CABA 22` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga CABA 28` | `Casa Oga CABA 28` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Cordoba 25` | `Casa Oga Cordoba 25` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Cordoba 7` | `Casa Oga Cordoba 7` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Entre Rios 17` | `Casa Oga Entre Rios 17` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Mendoza 1` | `Casa Oga Mendoza 1` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Mendoza 12` | `Casa Oga Mendoza 12` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Mendoza 19` | `Casa Oga Mendoza 19` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Mendoza 21` | `Casa Oga Mendoza 21` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Mendoza 3` | `Casa Oga Mendoza 3` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Neuquen 8` | `Casa Oga Neuquen 8` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Salta 15` | `Casa Oga Salta 15` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Salta 18` | `Casa Oga Salta 18` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Salta 26` | `Casa Oga Salta 26` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Santa Fe 13` | `Casa Oga Santa Fe 13` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Santa Fe 4` | `Casa Oga Santa Fe 4` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Santa Fe 6` | `Casa Oga Santa Fe 6` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Tucuman 16` | `Casa Oga Tucuman 16` | 1 |
| Tiendas | nombre_tienda | R1 sin tildes/enie | `Casa Óga Tucuman 9` | `Casa Oga Tucuman 9` | 1 |

**No se modificó** (pendiente de respuesta del negocio): valores negativos, nulos, duplicados por clave, fechas posteriores al corte ni descuentos fuera de rango.

