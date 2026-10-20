"""Reglas de negocio de limpieza de ventas.

Este módulo concentra la lógica de dominio del Microservicio 1:
validación, normalización, deduplicación y cálculo de totales.
No depende de FastAPI ni de Azure, por lo que se prueba de forma aislada.
"""

import pandas as pd

COLUMNAS_REQUERIDAS = {"id_venta", "fecha", "tienda", "producto", "cantidad", "precio"}


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """'ID Venta' -> 'id_venta'."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def limpiar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Aplica las reglas de negocio y devuelve (datos_limpios, resumen)."""
    df = normalizar_columnas(df)
    faltantes = COLUMNAS_REQUERIDAS - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {sorted(faltantes)}")

    recibidas = len(df)

    # Regla 1: toda venta debe tener identificador.
    df = df.dropna(subset=["id_venta"])
    sin_id = recibidas - len(df)

    # Regla 2: la cantidad debe ser un número positivo.
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    antes = len(df)
    df = df[df["cantidad"] > 0]
    cantidad_invalida = antes - len(df)

    # Regla 3: nombres de tienda homogéneos ("  norte " -> "Norte").
    df["tienda"] = df["tienda"].astype(str).str.strip().str.title()

    # Regla 4: fechas en formato ISO o latino (dd/mm/aaaa) a un único formato.
    iso = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")
    latino = pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce")
    df["fecha"] = iso.fillna(latino).dt.date
    antes = len(df)
    df = df.dropna(subset=["fecha"])
    fecha_invalida = antes - len(df)

    # Regla 5: una venta no puede registrarse dos veces.
    antes = len(df)
    df = df.drop_duplicates(subset=["id_venta"])
    duplicadas = antes - len(df)

    # Regla 6: total de la venta.
    df["total"] = df["cantidad"] * df["precio"]

    resumen = {
        "recibidas": recibidas,
        "cargadas": len(df),
        "descartadas": {
            "sin_id": sin_id,
            "cantidad_invalida": cantidad_invalida,
            "fecha_invalida": fecha_invalida,
            "duplicadas": duplicadas,
        },
    }
    return df.reset_index(drop=True), resumen
