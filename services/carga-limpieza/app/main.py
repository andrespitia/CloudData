"""Microservicio 1 - Carga y limpieza (esqueleto del hito 1).

La persistencia en Blob Storage y Azure SQL se implementa en hitos posteriores.
"""

import io

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile

from app.limpieza import limpiar

app = FastAPI(title="CloudData - Carga y limpieza", version="0.1.0")

LECTORES = {
    ".csv": pd.read_csv,
    ".xlsx": pd.read_excel,
    ".xml": pd.read_xml,
}


@app.get("/health")
def health():
    return {"estado": "ok", "servicio": "carga-limpieza"}


@app.post("/upload", status_code=201)
async def crear_carga(archivo: UploadFile):
    nombre = (archivo.filename or "").lower()
    extension = nombre[nombre.rfind("."):] if "." in nombre else ""
    if extension not in LECTORES:
        raise HTTPException(status_code=415, detail="Formato no soportado. Use CSV, XLSX o XML.")

    contenido = await archivo.read()
    try:
        datos = LECTORES[extension](io.BytesIO(contenido))
        _, resumen = limpiar(datos)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    # TODO (hito 2): guardar original en raw/, limpio en processed/ y cargar en Azure SQL.
    return {"archivo": archivo.filename, "estado": "procesado", **resumen}
