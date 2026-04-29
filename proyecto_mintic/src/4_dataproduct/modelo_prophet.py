import os
import sys
import warnings
from datetime import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error, mean_squared_error
import sqlalchemy

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB   = os.getenv("POSTGRES_DB",   "mintic_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "mintic_user")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "mintic2026")

RUTA_SERIE_CSV   = os.path.join("data", "processed", "serie_temporal_td.csv")
RUTA_GRAFICA     = os.path.join("data", "processed", "forecast_prophet.png")
MESES_PREDICCION = 6
PROPORCION_TEST  = 0.20


def crear_engine():
    from urllib.parse import quote_plus
    url = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{quote_plus(POSTGRES_PASS)}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        f"?client_encoding=utf8"
    )
    return sqlalchemy.create_engine(url)


def cargar_serie() -> pd.DataFrame:
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
    df = df[["fecha", "tasa_desocupacion"]].dropna()
    print(f"  Datos cargados desde CSV: {len(df)} registros")
    return df


def preparar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df_p = df.rename(columns={"fecha": "ds", "tasa_desocupacion": "y"})[["ds", "y"]].copy()
    df_p["ds"] = pd.to_datetime(df_p["ds"])
    return df_p.sort_values("ds").reset_index(drop=True)


def _entrenar_prophet(df_train, df_test, df_full):
    from prophet import Prophet

    def _modelo():
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

    m_eval = _modelo()
    m_eval.fit(df_train)
    n_test  = len(df_test)
    fc_eval = m_eval.predict(m_eval.make_future_dataframe(periods=n_test, freq="MS"))
    y_pred  = fc_eval.iloc[-n_test:]["yhat"].values

    m_full      = _modelo()
    m_full.fit(df_full)
    df_forecast = m_full.predict(m_full.make_future_dataframe(periods=MESES_PREDICCION, freq="MS"))

    return m_full, df_forecast, y_pred


def _entrenar_statsmodels(df_train, df_test, df_full):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from dateutil.relativedelta import relativedelta

    def _ajustar(serie, n_pred):
        modelo = ExponentialSmoothing(
            serie,
            trend="add",
            seasonal="add",
            seasonal_periods=12,
            initialization_method="estimated",
        ).fit(optimized=True)
        return modelo, modelo.forecast(n_pred)

    n_test = len(df_test)
    _, pred_test = _ajustar(df_train["y"], n_test)
    y_pred = pred_test.values

    modelo_full, pred_full = _ajustar(df_full["y"], MESES_PREDICCION)

    ultima_fecha   = df_full["ds"].max()
    fechas_futuras = [ultima_fecha + relativedelta(months=i + 1) for i in range(MESES_PREDICCION)]
    margen         = pred_full.std() * 1.645
    df_forecast = pd.DataFrame({
        "ds":         fechas_futuras,
        "yhat":       pred_full.values,
        "yhat_lower": pred_full.values - margen,
        "yhat_upper": pred_full.values + margen,
    })

    return modelo_full, df_forecast, y_pred


def entrenar_y_evaluar(df_prophet):
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

    return modelo_obj, df_forecast, mae, rmse, nombre_modelo


def guardar_predicciones(df_forecast, mae, rmse, nombre_modelo):
    df_pred = df_forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(MESES_PREDICCION).copy()
    df_pred = df_pred.rename(columns={"ds": "fecha"})
    df_pred.columns              = ["fecha", "td_predicha", "td_lower", "td_upper"]
    df_pred["fecha"]             = df_pred["fecha"].dt.date
    df_pred["td_predicha"]       = df_pred["td_predicha"].round(2).clip(0, 100)
    df_pred["td_lower"]          = df_pred["td_lower"].round(2).clip(0, 100)
    df_pred["td_upper"]          = df_pred["td_upper"].round(2).clip(0, 100)
    df_pred["mae"]               = round(mae, 4)
    df_pred["rmse"]              = round(rmse, 4)
    df_pred["modelo"]            = nombre_modelo
    df_pred["fecha_generado"]    = datetime.now()

    try:
        engine = crear_engine()
        with engine.begin() as conn:
            conn.execute(
                sqlalchemy.text("DELETE FROM prediccion_td WHERE modelo = :m"),
                {"m": nombre_modelo},
            )
            df_pred.to_sql("prediccion_td", conn, if_exists="append", index=False, method="multi")
        print(f"  ✓ {len(df_pred)} predicciones guardadas en PostgreSQL")
    except Exception as e:
        print(f"  ⚠ No se pudo guardar en PostgreSQL: {e}")
        ruta_csv = os.path.join("data", "processed", "prediccion_td.csv")
        df_pred.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
        print(f"  ✓ Respaldo guardado en: {ruta_csv}")


def graficar_forecast(modelo, df_forecast):
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        matplotlib.use("Agg")

        try:
            fig = modelo.plot(df_forecast, figsize=(12, 5))
        except AttributeError:
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df_forecast["ds"], df_forecast["yhat"], label="Forecast", color="steelblue")
            ax.fill_between(
                df_forecast["ds"],
                df_forecast["yhat_lower"],
                df_forecast["yhat_upper"],
                alpha=0.3, color="steelblue", label="Intervalo 80%",
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


def imprimir_predicciones(df_forecast):
    df_pred = df_forecast.tail(MESES_PREDICCION)
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


def entrenar_modelo():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando modelo de predicción...\n")

    df_raw     = cargar_serie()
    df_prophet = preparar_dataframe(df_raw)

    print(f"\n  Serie: {df_prophet['ds'].min().date()} → {df_prophet['ds'].max().date()}")
    print(f"  Puntos de entrenamiento: {len(df_prophet)}\n")

    modelo, df_forecast, mae, rmse, nombre_modelo = entrenar_y_evaluar(df_prophet)

    imprimir_predicciones(df_forecast)
    guardar_predicciones(df_forecast, mae, rmse, nombre_modelo)
    graficar_forecast(modelo, df_forecast)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Modelo completado.")
    print(f"  MAE = {mae:.4f} pp  |  RMSE = {rmse:.4f} pp")


if __name__ == "__main__":
    entrenar_modelo()
