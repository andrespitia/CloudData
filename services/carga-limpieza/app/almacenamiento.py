"""Capa de persistencia del Microservicio 1.

Guarda:
  - el archivo original en  <DATA_DIR>/raw/
  - el archivo depurado en   <DATA_DIR>/processed/
  - las ventas consolidadas y el historial de cargas en <DATA_DIR>/clouddata.db (SQLite)

En Docker Compose, DATA_DIR es un volumen compartido con el Microservicio 2.
En la nube, este módulo se reemplaza por Azure Blob Storage y Azure SQL
sin cambiar los endpoints.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def _directorio_por_defecto() -> Path:
    """Carpeta data/ en la raíz del repositorio al ejecutar sin Docker."""
    padres = Path(__file__).resolve().parents
    return padres[3] / "data" if len(padres) > 3 else Path("/data")


def data_dir() -> Path:
    return Path(os.getenv("DATA_DIR") or _directorio_por_defecto())


def ruta_db() -> Path:
    return data_dir() / "clouddata.db"


def conectar() -> sqlite3.Connection:
    data_dir().mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(ruta_db(), timeout=30)


def inicializar() -> None:
    """Crea carpetas y tablas si no existen."""
    for carpeta in ("raw", "processed"):
        (data_dir() / carpeta).mkdir(parents=True, exist_ok=True)
    with conectar() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS ventas (
                   id_venta TEXT PRIMARY KEY,
                   fecha    TEXT NOT NULL,
                   tienda   TEXT NOT NULL,
                   producto TEXT NOT NULL,
                   cantidad INTEGER NOT NULL,
                   precio   REAL NOT NULL,
                   total    REAL NOT NULL,
                   id_carga TEXT NOT NULL
               )"""
        )
        con.execute(
            """CREATE TABLE IF NOT EXISTS cargas (
                   id_carga    TEXT PRIMARY KEY,
                   archivo     TEXT NOT NULL,
                   fecha_carga TEXT NOT NULL,
                   resumen     TEXT NOT NULL
               )"""
        )


def guardar_original(id_carga: str, nombre: str, contenido: bytes) -> Path:
    destino = data_dir() / "raw" / f"{id_carga}_{Path(nombre).name}"
    destino.write_bytes(contenido)
    return destino


def guardar_procesado(id_carga: str, nombre: str, datos: pd.DataFrame) -> Path:
    destino = data_dir() / "processed" / f"{id_carga}_{Path(nombre).stem}.csv"
    datos.to_csv(destino, index=False)
    return destino


def insertar_ventas(id_carga: str, datos: pd.DataFrame) -> tuple[int, int]:
    """Inserta solo las ventas nuevas. Devuelve (insertadas, ya_existentes)."""
    if datos.empty:
        return 0, 0
    filas = [
        (
            str(f.id_venta), str(f.fecha), str(f.tienda), str(f.producto),
            int(f.cantidad), float(f.precio), float(f.total), id_carga,
        )
        for f in datos.itertuples(index=False)
    ]
    with conectar() as con:
        antes = con.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
        con.executemany(
            "INSERT OR IGNORE INTO ventas "
            "(id_venta, fecha, tienda, producto, cantidad, precio, total, id_carga) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            filas,
        )
        despues = con.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
    insertadas = despues - antes
    return insertadas, len(filas) - insertadas


def registrar_carga(id_carga: str, archivo: str, resumen: dict) -> None:
    with conectar() as con:
        con.execute(
            "INSERT INTO cargas (id_carga, archivo, fecha_carga, resumen) VALUES (?, ?, ?, ?)",
            (id_carga, archivo, datetime.now(timezone.utc).isoformat(timespec="seconds"),
             json.dumps(resumen, ensure_ascii=False)),
        )


def obtener_carga(id_carga: str) -> dict | None:
    with conectar() as con:
        fila = con.execute(
            "SELECT resumen FROM cargas WHERE id_carga = ?", (id_carga,)
        ).fetchone()
    return json.loads(fila[0]) if fila else None


def hay_ventas() -> bool:
    with conectar() as con:
        return con.execute("SELECT COUNT(*) FROM ventas").fetchone()[0] > 0
