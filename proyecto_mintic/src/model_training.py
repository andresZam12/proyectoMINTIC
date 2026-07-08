"""Entrenamiento y serialización del modelo de predicción."""
import pickle
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from src.config import MODEL_CONFIG, MODELS_DIR, DATA_OUTPUT


def train_holtwinters(serie: pd.Series) -> ExponentialSmoothing:
    """Entrena el modelo Holt-Winters con la serie completa."""
    model = ExponentialSmoothing(
        serie,
        trend=MODEL_CONFIG["trend"],
        seasonal=MODEL_CONFIG["seasonal"],
        seasonal_periods=MODEL_CONFIG["seasonal_periods"],
        initialization_method="estimated",
    ).fit(optimized=True)
    return model


def try_prophet(serie: pd.Series):
    """Intenta entrenar Prophet; retorna None si no está disponible."""
    try:
        from prophet import Prophet
        df_p = serie.reset_index()
        df_p.columns = ["ds", "y"]
        m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        m.fit(df_p)
        return m
    except Exception:
        return None


def generate_forecast(model, horizon: int, serie: pd.Series) -> pd.DataFrame:
    """Genera el forecast y calcula el intervalo de confianza empírico."""
    forecast = model.forecast(horizon)
    fitted = model.fittedvalues
    std_error = np.std(serie.values - fitted.values)
    z = 1.645  # IC 90%

    df_pred = pd.DataFrame({
        "fecha": forecast.index,
        "td_predicha": forecast.values.round(2),
        "td_lower": (forecast.values - z * std_error).round(2),
        "td_upper": (forecast.values + z * std_error).round(2),
        "modelo": "holt-winters",
    })
    return df_pred


def save_model(model, name: str = "holt_winters_td.pkl") -> str:
    """Serializa el modelo entrenado en la carpeta models/."""
    path = MODELS_DIR / name
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"Modelo guardado: {path}")
    return str(path)


def load_model(name: str = "holt_winters_td.pkl"):
    """Carga un modelo serializado."""
    path = MODELS_DIR / name
    with open(path, "rb") as f:
        return pickle.load(f)
