"""Microservicio 2 - Reportes / KPI."""

from fastapi import FastAPI, Query

from app import kpi
from app.datos import obtener_ventas

app = FastAPI(title="CloudData - Reportes", version="1.0.0")


@app.get("/health")
def health():
    return {"estado": "ok", "servicio": "reportes"}


@app.get("/kpi/ventas")
def kpi_ventas():
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
