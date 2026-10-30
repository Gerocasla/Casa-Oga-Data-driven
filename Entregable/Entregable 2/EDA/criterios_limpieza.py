# -*- coding: utf-8 -*-
"""
Criterios de limpieza de Ventas y Stock compartidos por el pipeline del modelo y los dashboards
(Entregable 2 · Parte B §1.2 y §2.1). Antes cada script repetia su propia copia de estas reglas.

H1 · deduplicacion por clave (mes, tienda, SKU)
    "mayor_venta" (v4, regla sugerida por Casa Oga en el relevamiento, P4: "quedarse con el registro que
                   tiene venta real / el de mayor venta por combinacion y descartar el que esta en cero").
                   Entre las filas no negativas de la clave se conserva la de mayor venta_neta (empate: la 1ra).
                   Ventas y Stock vienen alineados fila a fila (misma clave en la misma fila), asi que el stock
                   que se conserva es el de la misma fila que la venta elegida: los dos registros salen del
                   mismo origen (sistema anterior o nuevo, ver P4).
    "primera"     (v1-v3) 1ra ocurrencia en cada archivo por separado.
H4 · stock negativo -> 0 (P16) y ventas negativas (devoluciones) neteadas contra el mismo SKU-tienda-mes (P23).
    v4: el motivo "Producto sin rotacion / no vendido" NO se netea. Es una devolucion al proveedor (P18) que
    el negocio reconoce como movimiento de inventario y no como venta (P19): restarla bajaria el ritmo de venta
    de posiciones que no perdieron demanda. La fila queda con 0 unidades y $0 (la clave no desaparece del panel).
    El motivo se toma de Devoluciones_SKU, que coincide una a una con las filas negativas de Ventas.
"""
import pandas as pd

K = ["fecha_mes", "id_tienda", "id_producto"]
REGLA_DEDUP = "mayor_venta"
MOTIVO_SIN_ROTACION = "Producto sin rotacion / no vendido"


def motivos_devolucion(dev):
    """Devoluciones_SKU agregada a (mes, tienda, SKU) con su motivo (una devolucion por clave en los datos)."""
    d = dev.copy()
    d["fecha_mes"] = pd.to_datetime(d["fecha"]).dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m-%d")
    g = d.groupby(K).agg(unidades_devueltas=("unidades_devueltas", "sum"), motivo=("motivo", "first"),
                         n=("motivo", "size")).reset_index()
    assert (g["n"] == 1).all(), "se esperaba una devolucion por clave"
    return g.drop(columns="n")


def ventas_brutas(v_raw, regla=REGLA_DEDUP):
    """Filas de venta no negativas, una por clave segun la regla H1 (venta bruta, sin devoluciones)."""
    pos = v_raw[v_raw["unidades_vendidas"] >= 0]
    if regla == "primera": return pos.drop_duplicates(K)
    return pos.sort_values("venta_neta", ascending=False, kind="mergesort").drop_duplicates(K).sort_index()


def limpiar_ventas_stock(v_raw, s_raw, dev=None, regla=REGLA_DEDUP, excluir_sin_rotacion=True, info=None):
    """Devuelve (ventas por clave, stock por clave) con los criterios H1 y H4.

    v_raw, s_raw : Ventas y Stock tal como estan en Datasets_Normalizados (alineados fila a fila).
    dev          : Devoluciones_SKU (obligatorio si excluir_sin_rotacion).
    info         : dict opcional donde se dejan los conteos de control.
    """
    assert len(v_raw) == len(s_raw) and (v_raw[K].to_numpy() == s_raw[K].to_numpy()).all(), \
        "Ventas y Stock deben venir alineados fila a fila"
    neg = v_raw[v_raw["unidades_vendidas"] < 0].copy()
    pos_k = ventas_brutas(v_raw, regla)
    if regla == "primera":
        s = s_raw.drop_duplicates(K).copy()
    elif regla == "mayor_venta":
        # stock de la misma fila que la venta elegida; claves sin venta no negativa: 1ra ocurrencia
        sin_pos = s_raw.loc[neg.index].merge(pos_k[K], on=K, how="left", indicator=True)
        sin_pos_idx = neg.index[(sin_pos["_merge"] == "left_only").to_numpy()]
        s = s_raw.loc[pos_k.index.union(sin_pos_idx)].drop_duplicates(K).copy()
    else:
        raise ValueError(regla)
    if excluir_sin_rotacion:
        mot = motivos_devolucion(dev)
        neg = neg.merge(mot[K + ["unidades_devueltas", "motivo"]], on=K, how="left")
        assert neg["motivo"].notna().all() and (-neg["unidades_vendidas"] == neg["unidades_devueltas"]).all()
        sr = neg["motivo"] == MOTIVO_SIN_ROTACION
        if info is not None:
            info["sin_rotacion_filas"] = int(sr.sum())
            info["sin_rotacion_unidades"] = int(-neg.loc[sr, "unidades_vendidas"].sum())
            info["sin_rotacion_venta"] = float(-neg.loc[sr, "venta_neta"].sum())
        neg.loc[sr, ["unidades_vendidas", "venta_neta"]] = 0   # movimiento de inventario, no venta
        neg = neg.drop(columns=["unidades_devueltas", "motivo"])
    v = pd.concat([pos_k, neg]).groupby(K, as_index=False)[["unidades_vendidas", "venta_neta"]].sum()
    s["stock_disponible"] = s["stock_disponible"].clip(lower=0)
    if info is not None:
        info["filas_ventas"] = len(v); info["filas_stock"] = len(s)
    return v, s.reset_index(drop=True)
