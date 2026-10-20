"""Lectura de la capa de persistencia para el Microservicio 2 (solo lectura).

Lee las ventas consolidadas que escribe el Microservicio 1 en
<DATA_DIR>/clouddata.db. En la nube se reemplaza por Azure SQL.
"""

import os
import sqlite3
from pathlib import Path

import pandas as pd

COLUMNAS = ["id_venta", "fecha", "tienda", "producto", "cantidad", "precio", "total"]


def _directorio_por_defecto() -> Path:
    """Carpeta data/ en la raíz del repositorio al ejecutar sin Docker."""
    padres = Path(__file__).resolve().parents
    return padres[3] / "data" if len(padres) > 3 else Path("/data")


def ruta_db() -> Path:
    return Path(os.getenv("DATA_DIR") or _directorio_por_defecto()) / "clouddata.db"


def obtener_ventas() -> pd.DataFrame:
    """Devuelve las ventas consolidadas; vacío si aún no hay cargas."""
    ruta = ruta_db()
    if not ruta.exists():
        return pd.DataFrame(columns=COLUMNAS)
    # Modo solo lectura: el Microservicio 2 nunca modifica los datos.
    con = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True, timeout=30)
    try:
        tablas = {fila[0] for fila in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "ventas" not in tablas:
            return pd.DataFrame(columns=COLUMNAS)
        return pd.read_sql_query(f"SELECT {', '.join(COLUMNAS)} FROM ventas", con)
    finally:
        con.close()
