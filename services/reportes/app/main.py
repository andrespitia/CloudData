"""Microservicio 2 - Reportes / KPI (esqueleto del hito 1).

En este hito los datos se leen de un CSV de ventas consolidadas
(variable VENTAS_FUENTE). En hitos posteriores se reemplaza por
una consulta a Azure SQL Database, sin cambiar los endpoints.
"""

import os

import pandas as pd
from fastapi import FastAPI, Query

from app import kpi

app = FastAPI(title="CloudData - Reportes", version="0.1.0")

FUENTE = os.getenv("VENTAS_FUENTE", "datos/ventas_consolidadas.csv")


def obtener_ventas() -> pd.DataFrame:
    # TODO (hito 2): leer desde Azure SQL Database.
    return pd.read_csv(FUENTE)


@app.get("/health")
def health():
    return {"estado": "ok", "servicio": "reportes"}


@app.get("/kpi/ventas")
def kpi_resumen():
    return kpi.resumen(obtener_ventas())


@app.get("/kpi/ventas-por-tienda")
def kpi_ventas_por_tienda():
    return kpi.ventas_por_tienda(obtener_ventas())


@app.get("/kpi/top-productos")
def kpi_top_productos(limite: int = Query(5, ge=1, le=50)):
    return kpi.top_productos(obtener_ventas(), limite)


@app.get("/kpi/ventas-por-dia")
def kpi_ventas_por_dia(desde: str | None = None, hasta: str | None = None):
    return kpi.ventas_por_dia(obtener_ventas(), desde, hasta)
