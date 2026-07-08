"""Pruebas de consistencia en la predicción del modelo."""
import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

SERIE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "serie_temporal_td.csv")
PRED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "04_model_output", "prediccion_td.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "holt_winters_td.pkl")

MAE_THRESHOLD = 1.0
RMSE_THRESHOLD = 1.5
TD_MIN = 3.0
TD_MAX = 25.0


@pytest.fixture
def df_pred():
    if not os.path.exists(PRED_PATH):
        pytest.skip("prediccion_td.csv no encontrado — ejecutar modelo_prophet.py o notebook 04 primero")
    return pd.read_csv(PRED_PATH, parse_dates=["fecha"])


@pytest.fixture
def df_serie():
    if not os.path.exists(SERIE_PATH):
        pytest.skip("serie_temporal_td.csv no encontrado")
    return pd.read_csv(SERIE_PATH, parse_dates=["fecha"])


class TestPrediccionEstructura:
    def test_columnas_requeridas(self, df_pred):
        requeridas = {"fecha", "td_predicha", "td_lower", "td_upper"}
        assert requeridas.issubset(set(df_pred.columns))

    def test_horizonte_forecast(self, df_pred):
        assert len(df_pred) >= 6, f"Se esperaban ≥6 predicciones, hay {len(df_pred)}"

    def test_predicciones_en_rango_razonable(self, df_pred):
        assert (df_pred["td_predicha"] >= TD_MIN).all(), "Predicciones por debajo del mínimo esperado"
        assert (df_pred["td_predicha"] <= TD_MAX).all(), "Predicciones por encima del máximo esperado"

    def test_intervalo_coherente(self, df_pred):
        assert (df_pred["td_lower"] <= df_pred["td_predicha"]).all(), "Límite inferior > predicción"
        assert (df_pred["td_upper"] >= df_pred["td_predicha"]).all(), "Límite superior < predicción"

    def test_fechas_futuras(self, df_pred, df_serie):
        ultima_fecha = pd.to_datetime(df_serie["fecha"]).max()
        fechas_pred = pd.to_datetime(df_pred["fecha"])
        assert (fechas_pred > ultima_fecha).all(), "Las predicciones no son posteriores al último dato histórico"


class TestMetricasModelo:
    def test_mae_dentro_umbral(self, df_pred):
        if "mae" not in df_pred.columns:
            pytest.skip("Columna 'mae' no encontrada en predicciones")
        mae = df_pred["mae"].iloc[0]
        assert mae <= MAE_THRESHOLD, f"MAE={mae:.4f} supera el umbral de {MAE_THRESHOLD} pp"

    def test_rmse_dentro_umbral(self, df_pred):
        if "rmse" not in df_pred.columns:
            pytest.skip("Columna 'rmse' no encontrada en predicciones")
        rmse = df_pred["rmse"].iloc[0]
        assert rmse <= RMSE_THRESHOLD, f"RMSE={rmse:.4f} supera el umbral de {RMSE_THRESHOLD} pp"

    def test_mae_menor_que_rmse(self, df_pred):
        if "mae" not in df_pred.columns or "rmse" not in df_pred.columns:
            pytest.skip("Columnas mae/rmse no encontradas")
        assert df_pred["mae"].iloc[0] <= df_pred["rmse"].iloc[0], "MAE debe ser ≤ RMSE"
