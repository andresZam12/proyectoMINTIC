"""Pruebas de calidad de datos: rangos, nulos y tipos."""
import os
import sys
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

SERIE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "serie_temporal_td.csv")
SENA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "sena", "sena_inscritos.csv")

VALIDATION_RANGES = {
    "tasa_desocupacion": (5.0, 25.0),
    "tasa_ocupacion": (45.0, 70.0),
    "tasa_global_participacion": (55.0, 80.0),
}


@pytest.fixture
def df_serie():
    if not os.path.exists(SERIE_PATH):
        pytest.skip("serie_temporal_td.csv no encontrado — ejecutar parsear_boletines.py primero")
    return pd.read_csv(SERIE_PATH, parse_dates=["fecha"])


@pytest.fixture
def df_sena():
    if not os.path.exists(SENA_PATH):
        pytest.skip("sena_inscritos.csv no encontrado — ejecutar extraccion_sena.py primero")
    return pd.read_csv(SENA_PATH)


class TestSerieTemporal:
    def test_columnas_requeridas(self, df_serie):
        requeridas = {"fecha", "tasa_desocupacion", "tasa_ocupacion", "tasa_global_participacion"}
        assert requeridas.issubset(set(df_serie.columns)), f"Faltan columnas: {requeridas - set(df_serie.columns)}"

    def test_minimo_registros(self, df_serie):
        assert len(df_serie) >= 12, f"Se esperaban ≥12 registros, hay {len(df_serie)}"

    def test_sin_nulos_criticos(self, df_serie):
        for col in ["tasa_desocupacion", "tasa_ocupacion", "tasa_global_participacion"]:
            nulos = df_serie[col].isnull().sum()
            assert nulos == 0, f"{col} tiene {nulos} valores nulos"

    def test_rangos_validos(self, df_serie):
        for col, (vmin, vmax) in VALIDATION_RANGES.items():
            fuera = df_serie[(df_serie[col] < vmin) | (df_serie[col] > vmax)]
            assert len(fuera) == 0, f"{col}: {len(fuera)} valores fuera de rango [{vmin}, {vmax}]"

    def test_fechas_ordenadas(self, df_serie):
        fechas = pd.to_datetime(df_serie["fecha"])
        assert fechas.is_monotonic_increasing, "Las fechas no están en orden cronológico"

    def test_sin_fechas_duplicadas(self, df_serie):
        duplicados = df_serie["fecha"].duplicated().sum()
        assert duplicados == 0, f"Hay {duplicados} fechas duplicadas"

    def test_tipo_fecha(self, df_serie):
        assert pd.api.types.is_datetime64_any_dtype(df_serie["fecha"]), "La columna 'fecha' debe ser datetime"


class TestSena:
    def test_tiene_registros(self, df_sena):
        assert len(df_sena) > 0, "El dataset SENA está vacío"

    def test_columna_ocupacion_existe(self, df_sena):
        tiene = any("ocupaci" in c.lower() for c in df_sena.columns)
        assert tiene, "No se encontró columna de ocupación en el dataset SENA"

    def test_inscritos_no_negativos(self, df_sena):
        for col in df_sena.columns:
            if "inscritos" in col.lower() or "2019" in col or "2020" in col:
                vals = pd.to_numeric(df_sena[col], errors="coerce").dropna()
                assert (vals >= 0).all(), f"Valores negativos en columna {col}"
