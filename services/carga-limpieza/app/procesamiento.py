"""Caso de uso principal del Microservicio 1: procesar un archivo de ventas.

Separado de FastAPI para poder usarlo desde el endpoint, desde la carga
inicial de ejemplos y desde las pruebas.
"""

import io
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from app import almacenamiento
from app.limpieza import limpiar

LECTORES = {
    ".csv": pd.read_csv,
    ".xlsx": pd.read_excel,
    ".xml": pd.read_xml,
}


class FormatoNoSoportado(Exception):
    pass


def nuevo_id_carga() -> str:
    marca = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"c-{marca}-{uuid.uuid4().hex[:6]}"


def procesar_archivo(nombre: str, contenido: bytes) -> dict:
    """Guarda el original, limpia, guarda el depurado y consolida en la base.

    Lanza FormatoNoSoportado si la extensión no es CSV, XLSX o XML,
    y ValueError si el archivo no tiene las columnas obligatorias.
    """
    extension = Path(nombre).suffix.lower()
    if extension not in LECTORES:
        raise FormatoNoSoportado("Formato no soportado. Use CSV, XLSX o XML.")

    datos = LECTORES[extension](io.BytesIO(contenido))
    limpio, resumen = limpiar(datos)

    id_carga = nuevo_id_carga()
    almacenamiento.guardar_original(id_carga, nombre, contenido)
    almacenamiento.guardar_procesado(id_carga, nombre, limpio)
    insertadas, existentes = almacenamiento.insertar_ventas(id_carga, limpio)

    resultado = {
        "id_carga": id_carga,
        "archivo": Path(nombre).name,
        "estado": "procesado",
        "recibidas": resumen["recibidas"],
        "cargadas": insertadas,
        "descartadas": {**resumen["descartadas"], "ya_registradas": existentes},
    }
    almacenamiento.registrar_carga(id_carga, Path(nombre).name, resultado)
    return resultado


def carga_inicial(carpeta: str | None) -> list[dict]:
    """Carga los archivos de ejemplo si la base todavía no tiene ventas."""
    if not carpeta or almacenamiento.hay_ventas():
        return []
    ruta = Path(carpeta)
    if not ruta.is_dir():
        return []
    resultados = []
    for archivo in sorted(ruta.iterdir()):
        if archivo.suffix.lower() in LECTORES:
            try:
                resultados.append(procesar_archivo(archivo.name, archivo.read_bytes()))
            except (FormatoNoSoportado, ValueError) as error:
                resultados.append({"archivo": archivo.name, "estado": f"error: {error}"})
    return resultados
