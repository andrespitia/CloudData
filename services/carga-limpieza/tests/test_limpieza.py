import pandas as pd

from app.limpieza import limpiar


def _datos_de_ejemplo():
    return pd.DataFrame(
        {
            "ID Venta": ["V001", "V002", "V002", "V003", None, "V004", "V005"],
            "Fecha": ["2026-10-01", "01/10/2026", "01/10/2026", "2026-10-02",
                      "2026-10-02", "2026-10-02", "2026-10-03"],
            "Tienda": ["Centro", "norte", "norte", " Centro ", "Sur", "Sur", "Norte"],
            "Producto": ["Mouse inalámbrico", "Teclado USB", "Teclado USB", "Mouse inalámbrico",
                         "Audífonos", "Audífonos", "Cable HDMI"],
            "Cantidad": [3, 2, 2, 1, 5, -2, 4],
            "Precio": [45000, 120000, 120000, 45000, 38000, 38000, 32000],
        }
    )


def test_descarta_filas_invalidas_y_duplicadas():
    limpio, resumen = limpiar(_datos_de_ejemplo())
    assert resumen["recibidas"] == 7
    assert resumen["cargadas"] == 4
    assert resumen["descartadas"] == {
        "sin_id": 1, "cantidad_invalida": 1, "fecha_invalida": 0, "duplicadas": 1,
    }
    assert list(limpio["id_venta"]) == ["V001", "V002", "V003", "V005"]


def test_normaliza_tiendas_y_fechas():
    limpio, _ = limpiar(_datos_de_ejemplo())
    assert set(limpio["tienda"]) == {"Centro", "Norte"}
    assert str(limpio.loc[1, "fecha"]) == "2026-10-01"


def test_calcula_total():
    limpio, _ = limpiar(_datos_de_ejemplo())
    assert limpio["total"].sum() == 548000


def test_falla_si_faltan_columnas():
    try:
        limpiar(pd.DataFrame({"id_venta": ["V1"]}))
    except ValueError as error:
        assert "Faltan columnas" in str(error)
    else:
        raise AssertionError("Se esperaba ValueError")
