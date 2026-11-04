#Esta es la prueba de integracion
#docker compose up -d --build --wait
# 

import json
import os
import urllib.request
import uuid

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("CLOUDDATA_E2E") != "1",
    reason="Requiere el entorno de Docker Compose (CLOUDDATA_E2E=1)",
)

CARGA = os.getenv("CARGA_URL", "http://localhost:8000")
REPORTES = os.getenv("REPORTES_URL", "http://localhost:8001")


def get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as respuesta:
        return json.load(respuesta)


def subir_csv(nombre: str, contenido: str) -> dict:
    limite = uuid.uuid4().hex
    cuerpo = (
        f"--{limite}\r\n"
        f'Content-Disposition: form-data; name="archivo"; filename="{nombre}"\r\n'
        "Content-Type: text/csv\r\n\r\n"
        f"{contenido}\r\n"
        f"--{limite}--\r\n"
    ).encode()
    peticion = urllib.request.Request(
        f"{CARGA}/upload",
        data=cuerpo,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={limite}"},
    )
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        assert respuesta.status == 201
        return json.load(respuesta)


def test_servicios_sanos():
    assert get(f"{CARGA}/health")["estado"] == "ok"
    assert get(f"{REPORTES}/health")["estado"] == "ok"


def test_carga_inicial_visible_en_reportes():
    assert get(f"{REPORTES}/kpi/ventas")["numero_ventas"] > 0


def test_carga_nueva_se_refleja_en_reportes():
    antes = get(f"{REPORTES}/kpi/ventas")["numero_ventas"]
    id_venta = f"IT-{uuid.uuid4().hex[:8]}"
    csv = (
        "id_venta,fecha,tienda,producto,cantidad,precio\n"
        f"{id_venta},2026-10-07,Centro,Monitor 24,1,650000\n"
    )
    carga = subir_csv("integracion.csv", csv)
    assert carga["cargadas"] == 1

    assert get(f"{REPORTES}/kpi/ventas")["numero_ventas"] == antes + 1
    assert get(f"{CARGA}/cargas/{carga['id_carga']}") == carga

    
    repetida = subir_csv("integracion.csv", csv)
    assert repetida["cargadas"] == 0
    assert repetida["descartadas"]["ya_registradas"] == 1