import os
import sqlite3
from pathlib import Path

import pandas as pd

COLUMNAS = ["id_venta", "fecha", "tienda", "producto", "cantidad", "precio", "total"]
CONSULTA = f"SELECT {', '.join(COLUMNAS)} FROM ventas"


def _directorio_por_defecto() -> Path:
    padres = Path(__file__).resolve().parents
    return padres[3] / "data" if len(padres) > 3 else Path("/data")


def database_url() -> str:
    return os.getenv("DATABASE_URL", "")


def usa_postgres() -> bool:
    return database_url().startswith(("postgresql://", "postgres://"))


def ruta_db() -> Path:
    return Path(os.getenv("DATA_DIR") or _directorio_por_defecto()) / "clouddata.db"


def _vacio() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNAS)


def _leer_postgres() -> pd.DataFrame:
    import psycopg

    with psycopg.connect(database_url(), connect_timeout=5) as con:
        # Solo lectura: el Microservicio 2 nunca modifica los datos.
        con.read_only = True
        cur = con.cursor()
        cur.execute("SELECT to_regclass('public.ventas')")
        if cur.fetchone()[0] is None:
            return _vacio()
        cur.execute(CONSULTA)
        return pd.DataFrame(cur.fetchall(), columns=COLUMNAS)


def _leer_sqlite() -> pd.DataFrame:
    ruta = ruta_db()
    if not ruta.exists():
        return _vacio()
    # Modo solo lectura: el Microservicio 2 nunca modifica los datos.
    con = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True, timeout=30)
    try:
        tablas = {f[0] for f in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "ventas" not in tablas:
            return _vacio()
        return pd.DataFrame(con.execute(CONSULTA).fetchall(), columns=COLUMNAS)
    finally:
        con.close()


def obtener_ventas() -> pd.DataFrame:
    return _leer_postgres() if usa_postgres() else _leer_sqlite()
