from pathlib import Path

import pytest

from app import almacenamiento
from app.procesamiento import FormatoNoSoportado, carga_inicial, procesar_archivo

CSV = (
    "ID Venta,Fecha,Tienda,Producto,Cantidad,Precio\n"
    "V001,2026-10-01,Centro,Mouse inalámbrico,3,45000\n"
    "V002,01/10/2026,norte,Teclado USB,2,120000\n"
    "V002,01/10/2026,norte,Teclado USB,2,120000\n"
    ",2026-10-02,Sur,Audífonos,5,38000\n"
).encode("utf-8")


@pytest.fixture(autouse=True)
def datos_temporales(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    almacenamiento.inicializar()
    return tmp_path


def test_procesa_y_persiste(datos_temporales):
    r = procesar_archivo("ventas.csv", CSV)
    assert r["recibidas"] == 4
    assert r["cargadas"] == 2
    assert r["descartadas"]["duplicadas"] == 1
    assert r["descartadas"]["sin_id"] == 1
    assert len(list((datos_temporales / "raw").iterdir())) == 1
    assert len(list((datos_temporales / "processed").iterdir())) == 1
    assert almacenamiento.obtener_carga(r["id_carga"]) == r


def test_no_duplica_entre_cargas():
    procesar_archivo("ventas.csv", CSV)
    segunda = procesar_archivo("ventas.csv", CSV)
    assert segunda["cargadas"] == 0
    assert segunda["descartadas"]["ya_registradas"] == 2


def test_rechaza_formato_no_soportado():
    with pytest.raises(FormatoNoSoportado):
        procesar_archivo("ventas.pdf", b"x")


def test_carga_inicial_solo_si_la_base_esta_vacia(tmp_path):
    ejemplos = tmp_path / "ejemplos"
    ejemplos.mkdir()
    (ejemplos / "ventas.csv").write_bytes(CSV)
    (ejemplos / "leeme.txt").write_text("se ignora")
    assert len(carga_inicial(str(ejemplos))) == 1
    assert carga_inicial(str(ejemplos)) == []


def test_obtener_carga_inexistente():
    assert almacenamiento.obtener_carga("no-existe") is None
