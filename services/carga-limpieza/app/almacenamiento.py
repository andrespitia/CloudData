import json
import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

# La base de datos se elige con la variable DATABASE_URL:
#   - postgresql://usuario:clave@host:5432/base  -> PostgreSQL



def _directorio_por_defecto() -> Path:
    padres = Path(__file__).resolve().parents
    return padres[3] / "data" if len(padres) > 3 else Path("/data")


def data_dir() -> Path:
    return Path(os.getenv("DATA_DIR") or _directorio_por_defecto())


def database_url() -> str:
    return os.getenv("DATABASE_URL", "")


def usa_postgres() -> bool:
    return database_url().startswith(("postgresql://", "postgres://"))


def ruta_db() -> Path:
    return data_dir() / "clouddata.db"


def _q(sql: str) -> str:
    
    return sql.replace("?", "%s") if usa_postgres() else sql


@contextmanager
def conexion():
    if usa_postgres():
        import psycopg

        con = psycopg.connect(database_url(), connect_timeout=5)
    else:
        data_dir().mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(ruta_db(), timeout=30)
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _contar(con, sql: str, parametros: tuple = ()) -> int:
    cur = con.cursor()
    cur.execute(_q(sql), parametros)
    return cur.fetchone()[0]


TABLAS = (
    """CREATE TABLE IF NOT EXISTS ventas (
           id_venta TEXT PRIMARY KEY,
           fecha    TEXT NOT NULL,
           tienda   TEXT NOT NULL,
           producto TEXT NOT NULL,
           cantidad INTEGER NOT NULL,
           precio   DOUBLE PRECISION NOT NULL,
           total    DOUBLE PRECISION NOT NULL,
           id_carga TEXT NOT NULL
       )""",
    """CREATE TABLE IF NOT EXISTS cargas (
           id_carga    TEXT PRIMARY KEY,
           archivo     TEXT NOT NULL,
           fecha_carga TEXT NOT NULL,
           resumen     TEXT NOT NULL
       )""",
)


def inicializar(intentos: int = 10, espera: float = 2.0) -> None:
    for carpeta in ("raw", "processed"):
        (data_dir() / carpeta).mkdir(parents=True, exist_ok=True)
    #reintenta por si la base de datos esta arrancada
    for intento in range(1, intentos + 1):
        try:
            with conexion() as con:
                cur = con.cursor()
                for sql in TABLAS:
                    cur.execute(sql)
            return
        except Exception:
            if intento == intentos:
                raise
            time.sleep(espera)


def guardar_original(id_carga: str, nombre: str, contenido: bytes) -> Path:
    destino = data_dir() / "raw" / f"{id_carga}_{Path(nombre).name}"
    destino.write_bytes(contenido)
    return destino


def guardar_procesado(id_carga: str, nombre: str, datos: pd.DataFrame) -> Path:
    destino = data_dir() / "processed" / f"{id_carga}_{Path(nombre).stem}.csv"
    datos.to_csv(destino, index=False)
    return destino


def insertar_ventas(id_carga: str, datos: pd.DataFrame) -> tuple[int, int]:
    if datos.empty:
        return 0, 0
    filas = [
        (
            str(f.id_venta), str(f.fecha), str(f.tienda), str(f.producto),
            int(f.cantidad), float(f.precio), float(f.total), id_carga,
        )
        for f in datos.itertuples(index=False)
    ]
    with conexion() as con:
        antes = _contar(con, "SELECT COUNT(*) FROM ventas")
        con.cursor().executemany(
            _q(
                "INSERT INTO ventas "
                "(id_venta, fecha, tienda, producto, cantidad, precio, total, id_carga) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT (id_venta) DO NOTHING"
            ),
            filas,
        )
        despues = _contar(con, "SELECT COUNT(*) FROM ventas")
    insertadas = despues - antes
    return insertadas, len(filas) - insertadas


def registrar_carga(id_carga: str, archivo: str, resumen: dict) -> None:
    with conexion() as con:
        con.cursor().execute(
            _q("INSERT INTO cargas (id_carga, archivo, fecha_carga, resumen) VALUES (?, ?, ?, ?)"),
            (
                id_carga,
                archivo,
                datetime.now(UTC).isoformat(timespec="seconds"),
                json.dumps(resumen, ensure_ascii=False),
            ),
        )


def obtener_carga(id_carga: str) -> dict | None:
    with conexion() as con:
        cur = con.cursor()
        cur.execute(_q("SELECT resumen FROM cargas WHERE id_carga = ?"), (id_carga,))
        fila = cur.fetchone()
    return json.loads(fila[0]) if fila else None


def hay_ventas() -> bool:
    with conexion() as con:
        return _contar(con, "SELECT COUNT(*) FROM ventas") > 0