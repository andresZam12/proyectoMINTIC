import os
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Configuración de Rutas
CSV_FALLBACK = os.path.join("proyecto_mintic", "data", "processed", "fact_mercado_laboral.csv")
PLOT_OUTPUT = os.path.join("proyecto_mintic", "data", "processed", "forecast_2026.png")

def obtener_datos():
    """
    Carga datos desde PostgreSQL (Docker) con fallback a CSV.
    """
    load_dotenv("proyecto_mintic/.env")
    
    # Credenciales solicitadas
    USER = os.getenv("POSTGRES_USER", "mintic_user")
    PASSWORD = os.getenv("POSTGRES_PASSWORD", "mintic2026")
    HOST = os.getenv("POSTGRES_HOST", "localhost")
    PORT = "5433" # Puerto específico solicitado
    DB = os.getenv("POSTGRES_DB", "mintic_db")
    
    try:
        print(f"[*] Conectando a PostgreSQL en el puerto {PORT}...")
        engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}')
        
        query = """
        SELECT fecha_corte AS ds, tasa_informalidad AS y
        FROM fact_mercado_laboral
        WHERE tasa_informalidad IS NOT NULL
        ORDER BY fecha_corte ASC
        """
        df = pd.read_sql(query, engine)
        print(f"[OK] {len(df)} registros cargados desde la base de datos.")
        return df, engine
    except Exception as e:
        print(f"[!] Error de conexión a DB: {e}")
        print(f"[*] Intentando cargar respaldo desde: {CSV_FALLBACK}")
        if os.path.exists(CSV_FALLBACK):
            df = pd.read_csv(CSV_FALLBACK)
            # Adaptar nombres para Prophet si el CSV tiene otros nombres
            if 'fecha_corte' in df.columns: df = df.rename(columns={'fecha_corte': 'ds'})
            if 'tasa_desocupacion' in df.columns: df = df.rename(columns={'tasa_desocupacion': 'y'})
            elif 'tasa_informalidad' in df.columns: df = df.rename(columns={'tasa_informalidad': 'y'}) # Respaldo de informalidad
            
            df['ds'] = pd.to_datetime(df['ds'])
            print(f"[OK] {len(df)} registros cargados desde CSV.")
            return df, None
        else:
            raise FileNotFoundError("No se encontró ni la base de datos ni el archivo de respaldo CSV.")

def entrenar_y_predecir(df):
    """
    Configura y entrena el modelo Prophet para predecir el 2026.
    """
    print("[*] Iniciando entrenamiento del modelo Prophet...")
    model = Prophet(yearly_seasonality=True, interval_width=0.95)
    model.fit(df)
    
    # Crear dataframe para el futuro (12 meses de 2026)
    future = model.make_future_dataframe(periods=12, freq='MS')
    forecast = model.predict(future)
    
    print("[OK] Predicción completada para los próximos 12 meses.")
    return model, forecast

def guardar_resultados(model, forecast, engine):
    """
    Persiste los resultados en DB y genera la visualización.
    """
    # 1. Guardar en Base de Datos si la conexión está disponible
    if engine:
        try:
            print("[*] Guardando predicciones en la tabla 'prediccion_prophet'...")
            forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_sql(
                'prediccion_prophet', engine, if_exists='replace', index=False
            )
            print("[SUCCESS] Datos guardados en PostgreSQL.")
        except Exception as e:
            print(f"[!] Error al guardar en DB: {e}")

    # 2. Generar y guardar gráfica
    print(f"[*] Generando gráfica de tendencia en: {PLOT_OUTPUT}")
    fig = model.plot(forecast)
    plt.title("Pronóstico del Mercado Laboral Colombiano - 2026")
    plt.xlabel("Fecha")
    plt.ylabel("Tasa (%)")
    plt.savefig(PLOT_OUTPUT)
    print("[SUCCESS] Gráfica exportada exitosamente.")

def main():
    print("=== PIPELINE DE IA: PREDICCIÓN MERCADO LABORAL 2026 ===")
    try:
        df, engine = obtener_datos()
        model, forecast = entrenar_y_predecir(df)
        guardar_resultados(model, forecast, engine)
        print("=====================================================")
    except Exception as e:
        print(f"[CRITICAL ERROR] El pipeline falló: {e}")

if __name__ == "__main__":
    main()
