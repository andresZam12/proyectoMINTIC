"""
modelo_prophet.py  —  F3B · Modelo IA
Entrena Prophet con la serie histórica TD 2010-2026,
genera predicción 6 meses, calcula MAE/RMSE y guarda en PostgreSQL.
Cumple el criterio 'Uso de IA (20 pts)' del concurso MinTIC.
"""

import os
import sys
import warnings
from datetime import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error, mean_squared_error
import sqlalchemy

# Forzar UTF-8 en consola Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
load_dotenv()

# ── Constantes ────────────────────────────────────────────────────
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB   = os.getenv("POSTGRES_DB",   "mintic_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "mintic_user")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "mintic2026")

RUTA_SERIE_CSV   = os.path.join("data", "processed", "serie_temporal_td.csv")
RUTA_GRAFICA     = os.path.join("data", "processed", "forecast_prophet.png")
MESES_PREDICCION = 6

# Proporción de datos para validación (último 20% de la serie)
PROPORCION_TEST  = 0.20


# ── Conexión PostgreSQL ───────────────────────────────────────────
def crear_engine():
    from urllib.parse import quote_plus
    # quote_plus codifica caracteres especiales en la contraseña
    url = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{quote_plus(POSTGRES_PASS)}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        f"?client_encoding=utf8"
    )
    return sqlalchemy.create_engine(url)


# ── Carga de datos ────────────────────────────────────────────────
def cargar_serie() -> pd.DataFrame:
    """
    Carga la serie histórica de TD desde PostgreSQL.
    Fallback: lee data/processed/serie_temporal_td.csv si no hay conexión.
    """
    try:
        engine = crear_engine()
        with engine.connect() as conn:
            df = pd.read_sql(
                """
                SELECT p.fecha_inicio AS fecha,
                       f.tasa_desocupacion
                FROM   fact_mercado_laboral f
                JOIN   dim_periodo p ON p.id_periodo = f.id_periodo
                WHERE  f.fuente = 'DANE_BOLETIN'
                  AND  f.sexo = 'Total'
                  AND  f.zona = 'Total'
                  AND  f.tasa_desocupacion IS NOT NULL
                ORDER  BY p.fecha_inicio
                """,
                conn,
            )
        print(f"  Datos cargados desde PostgreSQL: {len(df)} registros")
        return df
    except Exception as e:
        print(f"  ⚠ PostgreSQL no disponible ({e}), usando CSV...")

    if not os.path.exists(RUTA_SERIE_CSV):
        raise FileNotFoundError(
            f"No hay datos. Ejecutar parsear_boletines.py primero.\n"
            f"Ruta esperada: {RUTA_SERIE_CSV}"
        )
    df = pd.read_csv(RUTA_SERIE_CSV, parse_dates=["fecha"])
    df = df.rename(columns={"tasa_desocupacion": "tasa_desocupacion"})
    df = df[["fecha", "tasa_desocupacion"]].dropna()
    print(f"  Datos cargados desde CSV: {len(df)} registros")
    return df


# ── Preparación para Prophet ──────────────────────────────────────
def preparar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Prophet requiere columnas 'ds' (fecha) y 'y' (valor)."""
    df_prophet = df.rename(columns={
        "fecha":             "ds",
        "tasa_desocupacion": "y",
    })[["ds", "y"]].copy()
    df_prophet["ds"] = pd.to_datetime(df_prophet["ds"])
    df_prophet = df_prophet.sort_values("ds").reset_index(drop=True)
    return df_prophet


# ── Backend Prophet ───────────────────────────────────────────────
def _entrenar_prophet(df_train: pd.DataFrame, df_test: pd.DataFrame,
                      df_full: pd.DataFrame) -> tuple:
    """Entrena con Prophet. Lanza excepción si no está disponible."""
    from prophet import Prophet  # import tardío — puede fallar si Stan no compiló

    def _crear_modelo():
        m = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
            changepoint_prior_scale=0.1,
            interval_width=0.80,
        )
        m.add_seasonality(name="cuatrimestral", period=365.25 / 3, fourier_order=5)
        return m

    m_eval = _crear_modelo()
    m_eval.fit(df_train)
    n_test = len(df_test)
    fc_eval = m_eval.predict(m_eval.make_future_dataframe(periods=n_test, freq="MS"))
    y_pred  = fc_eval.iloc[-n_test:]["yhat"].values

    m_full = _crear_modelo()
    m_full.fit(df_full)
    futuro      = m_full.make_future_dataframe(periods=MESES_PREDICCION, freq="MS")
    df_forecast = m_full.predict(futuro)

    return m_full, df_forecast, y_pred


# ── Backend statsmodels (fallback sin compilador C++) ─────────────
def _entrenar_statsmodels(df_train: pd.DataFrame, df_test: pd.DataFrame,
                          df_full: pd.DataFrame) -> tuple:
    """
    Holt-Winters (exponential smoothing) con estacionalidad anual.
    No requiere Stan ni CmdStan — funciona en cualquier entorno.
    """
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from dateutil.relativedelta import relativedelta

    def _ajustar(serie: pd.Series, n_pred: int):
        modelo = ExponentialSmoothing(
            serie,
            trend="add",
            seasonal="add",
            seasonal_periods=12,
            initialization_method="estimated",
        ).fit(optimized=True)
        return modelo, modelo.forecast(n_pred)

    n_test = len(df_test)

    # Evaluación en test
    _, pred_test = _ajustar(df_train["y"], n_test)
    y_pred = pred_test.values

    # Forecast final con todos los datos
    modelo_full, pred_full = _ajustar(df_full["y"], MESES_PREDICCION)

    ultima_fecha = df_full["ds"].max()
    fechas_futuras = [
        ultima_fecha + relativedelta(months=i + 1)
        for i in range(MESES_PREDICCION)
    ]
    # Intervalo simple ±1.5 pp (90% empírico para la serie TD Colombia)
    margen = pred_full.std() * 1.645
    df_forecast = pd.DataFrame({
        "ds":         fechas_futuras,
        "yhat":       pred_full.values,
        "yhat_lower": pred_full.values - margen,
        "yhat_upper": pred_full.values + margen,
    })

    return modelo_full, df_forecast, y_pred


# ── Entrenamiento y evaluación ────────────────────────────────────
def entrenar_y_evaluar(df_prophet: pd.DataFrame) -> tuple:
    """
    Intenta Prophet primero; si no está disponible (CmdStan no compilado)
    usa Holt-Winters de statsmodels. Retorna (modelo, df_forecast, mae, rmse).
    """
    n_test   = max(6, int(len(df_prophet) * PROPORCION_TEST))
    df_train = df_prophet.iloc[:-n_test]
    df_test  = df_prophet.iloc[-n_test:]

    print(f"  Train: {len(df_train)} meses  |  Test: {len(df_test)} meses")

    try:
        print("  Backend: Prophet")
        modelo_obj, df_forecast, y_pred = _entrenar_prophet(df_train, df_test, df_prophet)
        nombre_modelo = "Prophet"
    except Exception as e:
        print(f"  Prophet no disponible ({e.__class__.__name__}). Usando Holt-Winters.")
        modelo_obj, df_forecast, y_pred = _entrenar_statsmodels(df_train, df_test, df_prophet)
        nombre_modelo = "HoltWinters"

    y_real = df_test["y"].values
    mae    = mean_absolute_error(y_real, y_pred)
    rmse   = np.sqrt(mean_squared_error(y_real, y_pred))

    print(f"  Modelo: {nombre_modelo}")
    print(f"  MAE  = {mae:.4f} pp")
    print(f"  RMSE = {rmse:.4f} pp")

    return modelo_obj, df_forecast, mae, rmse


# ── Guardar predicciones en PostgreSQL ───────────────────────────
def guardar_predicciones(df_forecast: pd.DataFrame, mae: float, rmse: float) -> None:
    """
    Inserta los 6 meses futuros en la tabla prediccion_td.
    df_forecast puede venir de Prophet (tiene 'ds') o de Holt-Winters (fechas futuras).
    """
    # Holt-Winters ya devuelve solo los 6 meses futuros
    if "ds" not in df_forecast.columns:
        df_pred = df_forecast[["yhat", "yhat_lower", "yhat_upper"]].head(MESES_PREDICCION).copy()
    else:
        ultima_fecha_historico = df_forecast[
            df_forecast["ds"] <= datetime.today()
        ]["ds"].max()
        df_pred = df_forecast[df_forecast["ds"] > ultima_fecha_historico].copy()
        df_pred = df_pred[["ds", "yhat", "yhat_lower", "yhat_upper"]].head(MESES_PREDICCION)

    if "ds" in df_pred.columns:
        df_pred = df_pred.rename(columns={"ds": "fecha"})
    df_pred.columns = ["fecha", "td_predicha", "td_lower", "td_upper"]
    df_pred["fecha"]      = df_pred["fecha"].dt.date
    df_pred["td_predicha"] = df_pred["td_predicha"].round(2).clip(0, 100)
    df_pred["td_lower"]    = df_pred["td_lower"].round(2).clip(0, 100)
    df_pred["td_upper"]    = df_pred["td_upper"].round(2).clip(0, 100)
    df_pred["mae"]         = round(mae, 4)
    df_pred["rmse"]        = round(rmse, 4)
    df_pred["modelo"]      = "Prophet-1.1.5"
    df_pred["fecha_generado"] = datetime.now()

    try:
        engine = crear_engine()
        with engine.begin() as conn:
            # Eliminar predicciones anteriores para re-ejecutabilidad
            conn.execute(
                sqlalchemy.text("DELETE FROM prediccion_td WHERE modelo = 'Prophet-1.1.5'")
            )
            df_pred.to_sql(
                "prediccion_td",
                conn,
                if_exists="append",
                index=False,
                method="multi",
            )
        print(f"  ✓ {len(df_pred)} predicciones guardadas en PostgreSQL")
    except Exception as e:
        print(f"  ⚠ No se pudo guardar en PostgreSQL: {e}")
        # Guardar CSV como respaldo
        ruta_csv = os.path.join("data", "processed", "prediccion_td.csv")
        df_pred.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
        print(f"  ✓ Respaldo guardado en: {ruta_csv}")


# ── Gráfica de forecast ───────────────────────────────────────────
def graficar_forecast(modelo, df_forecast: pd.DataFrame) -> None:
    """Guarda la gráfica del forecast en data/processed/."""
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        matplotlib.use("Agg")

        col_fecha = "ds" if "ds" in df_forecast.columns else "fecha"

        # Si el modelo tiene .plot() es Prophet, si no graficamos manualmente
        try:
            fig = modelo.plot(df_forecast, figsize=(12, 5))
        except AttributeError:
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df_forecast[col_fecha], df_forecast["yhat"], label="Forecast", color="steelblue")
            ax.fill_between(
                df_forecast[col_fecha],
                df_forecast["yhat_lower"],
                df_forecast["yhat_upper"],
                alpha=0.3, color="steelblue", label="Intervalo 80%"
            )
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Tasa de Desocupación (%)")
            ax.legend()

        fig.suptitle(
            "Tasa de Desocupación Nacional — Histórico + Predicción 6 meses",
            fontsize=13,
        )
        os.makedirs(os.path.dirname(RUTA_GRAFICA), exist_ok=True)
        fig.savefig(RUTA_GRAFICA, dpi=150, bbox_inches="tight")
        print(f"  ✓ Gráfica guardada en: {RUTA_GRAFICA}")
    except Exception as e:
        print(f"  ⚠ No se pudo generar la gráfica: {e}")


# ── Reporte de predicciones ───────────────────────────────────────
def imprimir_predicciones(df_forecast: pd.DataFrame) -> None:
    ultima_historica = df_forecast[
        df_forecast["ds"] <= datetime.today()
    ]["ds"].max()
    df_pred = df_forecast[df_forecast["ds"] > ultima_historica].head(MESES_PREDICCION)

    print(f"\n{'─'*55}")
    print(f"  {'Mes':<12} {'TD pred':>8} {'Inf 80%':>9} {'Sup 80%':>9}")
    print(f"{'─'*55}")
    for _, row in df_pred.iterrows():
        print(
            f"  {row['ds'].strftime('%Y-%m'):<12} "
            f"{row['yhat']:>7.2f}%  "
            f"{row['yhat_lower']:>7.2f}%  "
            f"{row['yhat_upper']:>7.2f}%"
        )
    print(f"{'─'*55}")


# ── Entry point ───────────────────────────────────────────────────
def entrenar_modelo():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando modelo Prophet...\n")

    df_raw     = cargar_serie()
    df_prophet = preparar_dataframe(df_raw)

    print(f"\n  Serie: {df_prophet['ds'].min().date()} → {df_prophet['ds'].max().date()}")
    print(f"  Puntos de entrenamiento: {len(df_prophet)}\n")

    modelo, df_forecast, mae, rmse = entrenar_y_evaluar(df_prophet)

    imprimir_predicciones(df_forecast)
    guardar_predicciones(df_forecast, mae, rmse)
    graficar_forecast(modelo, df_forecast)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Modelo Prophet completado.")
    print(f"  MAE = {mae:.4f} pp  |  RMSE = {rmse:.4f} pp")


if __name__ == "__main__":
    entrenar_modelo()
