import pandas as pd

from app import kpi


def _ventas():
    return pd.DataFrame(
        {
            "id_venta": ["V001", "V002", "V003", "V005"],
            "fecha": ["2026-10-01", "2026-10-01", "2026-10-02", "2026-10-03"],
            "tienda": ["Centro", "Norte", "Centro", "Norte"],
            "producto": ["Mouse inalámbrico", "Teclado USB", "Mouse inalámbrico", "Cable HDMI"],
            "cantidad": [3, 2, 1, 4],
            "precio": [45000, 120000, 45000, 32000],
            "total": [135000, 240000, 45000, 128000],
        }
    )


def test_resumen():
    assert kpi.resumen(_ventas()) == {
        "ventas_totales": 548000.0, "numero_ventas": 4, "ticket_promedio": 137000.0,
    }


def test_ventas_por_tienda_ordenadas_de_mayor_a_menor():
    assert kpi.ventas_por_tienda(_ventas()) == [
        {"tienda": "Norte", "total": 368000.0},
        {"tienda": "Centro", "total": 180000.0},
    ]


def test_top_productos_por_unidades():
    top = kpi.top_productos(_ventas(), limite=2)
    assert [p["producto"] for p in top] == ["Mouse inalámbrico", "Cable HDMI"]
    assert top[0]["unidades"] == 4


def test_ventas_por_dia_con_filtro():
    assert kpi.ventas_por_dia(_ventas(), desde="2026-10-02") == [
        {"fecha": "2026-10-02", "total": 45000.0},
        {"fecha": "2026-10-03", "total": 128000.0},
    ]
