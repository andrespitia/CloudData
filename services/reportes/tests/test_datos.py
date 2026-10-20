import sqlite3

from app import kpi
from app.datos import obtener_ventas


def test_sin_base_devuelve_vacio(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    ventas = obtener_ventas()
    assert ventas.empty
    assert kpi.resumen(ventas) == {"ventas_totales": 0.0, "numero_ventas": 0, "ticket_promedio": 0.0}
    assert kpi.ventas_por_tienda(ventas) == []
    assert kpi.ventas_por_dia(ventas) == []


def test_lee_ventas_consolidadas(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    con = sqlite3.connect(tmp_path / "clouddata.db")
    con.execute(
        "CREATE TABLE ventas (id_venta TEXT PRIMARY KEY, fecha TEXT, tienda TEXT, producto TEXT,"
        " cantidad INTEGER, precio REAL, total REAL, id_carga TEXT)"
    )
    con.executemany(
        "INSERT INTO ventas VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("V001", "2026-10-01", "Centro", "Mouse inalámbrico", 3, 45000, 135000, "c1"),
            ("V002", "2026-10-01", "Norte", "Teclado USB", 2, 120000, 240000, "c1"),
        ],
    )
    con.commit()
    con.close()
    ventas = obtener_ventas()
    assert kpi.resumen(ventas)["ventas_totales"] == 375000.0
    assert kpi.ventas_por_tienda(ventas)[0] == {"tienda": "Norte", "total": 240000.0}
