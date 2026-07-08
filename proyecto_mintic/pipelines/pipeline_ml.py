"""
Orquestador del pipeline completo de ML.
Ejecuta todas las etapas en orden: integración → features → entrenamiento → evaluación → forecast.
"""
import sys
import os
import pickle
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import MODEL_CONFIG, DATA_PRIMARY, DATA_OUTPUT, MODELS_DIR
from src.pipeline_integration import run_integration_pipeline
from src.feature_engineering import build_feature_matrix
from src.model_training import train_holtwinters, try_prophet, generate_forecast, save_model
from src.model_evaluation import evaluate_model, plot_forecast


def run_full_pipeline(save_plots: bool = True, verbose: bool = True) -> dict:
    """
    Ejecuta el pipeline ML completo.
    Retorna un diccionario con métricas y rutas de archivos generados.
    """
    print("=" * 55)
    print("  PIPELINE ML — Mercado Laboral Colombia")
    print("  Concurso Datos al Ecosistema 2026")
    print("=" * 55)

    # ── Paso 1: Integración de datos ──────────────────────
    print("\n[1/5] Integración y limpieza de datos...")
    df_consolidado = run_integration_pipeline()

    # ── Paso 2: Extraer serie temporal ────────────────────
    print("\n[2/5] Preparando serie temporal...")
    serie_path = DATA_PRIMARY / "dataset_consolidado.csv"
    df = pd.read_csv(serie_path, parse_dates=["fecha"])
    serie = df.set_index("fecha")["tasa_desocupacion"].sort_index()
    if verbose:
        print(f"  Puntos en serie: {len(serie)} | {serie.index.min().date()} → {serie.index.max().date()}")

    # ── Paso 3: Entrenamiento ─────────────────────────────
    print("\n[3/5] Entrenando modelo...")
    split = int(len(serie) * MODEL_CONFIG["train_ratio"])
    train, test = serie.iloc[:split], serie.iloc[split:]

    model = try_prophet(train)
    model_name = "prophet"
    if model is None:
        model = train_holtwinters(train)
        model_name = "holt-winters"
    print(f"  Modelo usado: {model_name}")

    # ── Paso 4: Evaluación ────────────────────────────────
    print("\n[4/5] Evaluando en conjunto de prueba...")
    pred_test = model.forecast(len(test))
    if hasattr(pred_test, "values"):
        pred_test_vals = pred_test
    else:
        pred_test_vals = pd.Series(pred_test["yhat"].values, index=test.index)

    metrics = evaluate_model(test, pred_test_vals)

    # ── Paso 5: Forecast final ────────────────────────────
    print("\n[5/5] Generando forecast a 6 meses...")
    model_final = train_holtwinters(serie)
    forecast_df = generate_forecast(model_final, MODEL_CONFIG["forecast_horizon"], serie)
    forecast_df["mae"] = metrics["mae"]
    forecast_df["rmse"] = metrics["rmse"]

    # Guardar predicciones
    output_path = DATA_OUTPUT / "prediccion_td.csv"
    forecast_df.to_csv(output_path, index=False)

    # Guardar modelo
    model_path = save_model(model_final)

    # Gráfica
    if save_plots:
        plot_forecast(train, test, pred_test_vals, forecast_df, metrics, save=True)

    print("\n" + "=" * 55)
    print("  Pipeline completado.")
    print(f"  MAE:  {metrics['mae']} pp  |  RMSE: {metrics['rmse']} pp")
    print(f"  Predicciones: {output_path}")
    print(f"  Modelo:       {model_path}")
    print("=" * 55)

    return {
        "metrics": metrics,
        "forecast": forecast_df,
        "model_path": model_path,
        "output_path": str(output_path),
    }


if __name__ == "__main__":
    results = run_full_pipeline()
