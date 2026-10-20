"""Cálculo de indicadores (KPI) de ventas.

Lógica de dominio del Microservicio 2. Recibe ventas ya consolidadas
(las que el Microservicio 1 deja en la capa de persistencia) y calcula
los indicadores que consume Power BI.
"""

import pandas as pd


def resumen(ventas: pd.DataFrame) -> dict:
    total = float(ventas["total"].sum())
    numero = int(len(ventas))
    return {
        "ventas_totales": total,
        "numero_ventas": numero,
        "ticket_promedio": round(total / numero, 2) if numero else 0.0,
    }


def ventas_por_tienda(ventas: pd.DataFrame) -> list[dict]:
    agrupado = (
        ventas.groupby("tienda", as_index=False)["total"].sum()
        .sort_values("total", ascending=False)
    )
    return [
        {"tienda": fila.tienda, "total": float(fila.total)}
        for fila in agrupado.itertuples()
    ]


def top_productos(ventas: pd.DataFrame, limite: int = 5) -> list[dict]:
    agrupado = (
        ventas.groupby("producto", as_index=False)
        .agg(unidades=("cantidad", "sum"), total=("total", "sum"))
        .sort_values(["unidades", "total"], ascending=False)
        .head(limite)
    )
    return [
        {"producto": fila.producto, "unidades": int(fila.unidades), "total": float(fila.total)}
        for fila in agrupado.itertuples()
    ]


def ventas_por_dia(ventas: pd.DataFrame, desde: str | None = None, hasta: str | None = None) -> list[dict]:
    datos = ventas.copy()
    datos["fecha"] = pd.to_datetime(datos["fecha"])
    if desde:
        datos = datos[datos["fecha"] >= pd.to_datetime(desde)]
    if hasta:
        datos = datos[datos["fecha"] <= pd.to_datetime(hasta)]
    agrupado = datos.groupby("fecha", as_index=False)["total"].sum().sort_values("fecha")
    return [
        {"fecha": fila.fecha.date().isoformat(), "total": float(fila.total)}
        for fila in agrupado.itertuples()
    ]
