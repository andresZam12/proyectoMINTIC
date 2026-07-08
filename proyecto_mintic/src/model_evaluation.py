"""Evaluación del modelo: métricas, visualizaciones y reporte."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.config import MODEL_CONFIG, FIGURES_DIR


def evaluate_model(y_true: pd.Series, y_pred: pd.Series) -> dict:
    """Calcula MAE y RMSE del modelo."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    meets_mae = mae <= MODEL_CONFIG["mae_threshold"]
    meets_rmse = rmse <= MODEL_CONFIG["rmse_threshold"]

    results = {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mae_ok": meets_mae,
        "rmse_ok": meets_rmse,
        "n_test": len(y_true),
    }

    print(f"MAE:  {mae:.4f} pp  {'✅' if meets_mae else '❌'} (umbral {MODEL_CONFIG['mae_threshold']} pp)")
    print(f"RMSE: {rmse:.4f} pp  {'✅' if meets_rmse else '❌'} (umbral {MODEL_CONFIG['rmse_threshold']} pp)")
    return results


def plot_forecast(train: pd.Series, test: pd.Series, pred_test: pd.Series,
                  forecast_df: pd.DataFrame, metrics: dict, save: bool = True):
    """Genera y guarda la gráfica del forecast."""
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(train.index, train.values, color="#2c3e50", lw=2, label="Entrenamiento")
    ax.plot(test.index, test.values, color="#e74c3c", lw=2, ls="--", label="Prueba (real)")
    ax.plot(pred_test.index, pred_test.values, color="#e67e22", lw=1.8, ls=":", label="Predicción prueba")
    ax.plot(forecast_df["fecha"], forecast_df["td_predicha"], color="#2980b9",
            lw=2.5, marker="o", ms=6, label="Forecast 6 meses")
    ax.fill_between(forecast_df["fecha"], forecast_df["td_lower"], forecast_df["td_upper"],
                    alpha=0.2, color="#2980b9", label="IC 90%")

    ax.axvline(test.index[0], color="gray", ls="--", lw=1, alpha=0.6)
    ax.set_title(f"Tasa de Desocupación Colombia — Holt-Winters\n"
                 f"MAE={metrics['mae']:.2f}pp | RMSE={metrics['rmse']:.2f}pp", fontsize=13)
    ax.set_ylabel("Tasa (%)")
    ax.legend(loc="upper right")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save:
        path = FIGURES_DIR / "forecast_modelo.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Gráfica guardada: {path}")
    plt.show()


def confusion_matrix_placeholder():
    """Placeholder — no aplica para regresión de series temporales."""
    print("Nota: la matriz de confusión aplica para clasificación. Este modelo es de regresión.")
    print("Usar MAE y RMSE como métricas de evaluación.")
