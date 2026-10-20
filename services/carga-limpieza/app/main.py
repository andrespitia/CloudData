"""Microservicio 1 - Carga y limpieza."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile

from app import almacenamiento
from app.procesamiento import FormatoNoSoportado, carga_inicial, procesar_archivo


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    almacenamiento.inicializar()
    
    carga_inicial(os.getenv("CARGA_INICIAL_DIR"))
    yield


app = FastAPI(title="CloudData - Carga y limpieza", version="1.0.0", lifespan=ciclo_de_vida)


@app.get("/health")
def health():
    return {"estado": "ok", "servicio": "carga-limpieza"}


@app.post("/upload", status_code=201)
async def upload(archivo: UploadFile):
    contenido = await archivo.read()
    try:
        return procesar_archivo(archivo.filename or "archivo", contenido)
    except FormatoNoSoportado as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/cargas/{id_carga}")
def obtener_carga(id_carga: str):
    resumen = almacenamiento.obtener_carga(id_carga)
    if resumen is None:
        raise HTTPException(status_code=404, detail="La carga no existe.")
    return resumen
