import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv("proyecto_mintic/.env")

def obtener_engine():
    USER = os.getenv("POSTGRES_USER", "mintic_user")
    PASSWORD = os.getenv("POSTGRES_PASSWORD", "mintic2026")
    HOST = os.getenv("POSTGRES_HOST", "localhost")
    PORT = "5433"
    DB = os.getenv("POSTGRES_DB", "mintic_db")
    return create_engine(f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}')

def cargar_dim_periodo(engine):
    print("[*] Generando Dimension de Periodos (Calendario)...")
    # Generar rango desde 2022 hasta 2027
    fechas = pd.date_range(start="2022-01-01", end="2027-12-01", freq="MS")
    df_periodo = pd.DataFrame({
        'id_periodo': range(1, len(fechas) + 1),
        'fecha_inicio': fechas,
        'anio': fechas.year,
        'mes': fechas.month,
        'trimestre': fechas.quarter
    })
    df_periodo.to_sql('dim_periodo', engine, if_exists='replace', index=False)
    print("[OK] dim_periodo cargada.")

def cargar_predicciones_boletines(engine):
    print("[*] Cargando datos de Boletines (TD)...")
    path_td = "proyecto_mintic/data/processed/serie_temporal_td.csv"
    if os.path.exists(path_td):
        df_td = pd.read_csv(path_td)
        # Ajustar columnas si es necesario para que coincida con la tabla
        df_td.to_sql('prediccion_td', engine, if_exists='replace', index=False)
        print("[OK] prediccion_td cargada.")
    else:
        print("[!] No se encontró serie_temporal_td.csv")

def cargar_dim_departamento(engine):
    print("[*] Cargando Dimension de Departamentos...")
    # Lista estandarizada de Colombia
    deptos = [
        "AMAZONAS", "ANTIOQUIA", "ARAUCA", "ATLANTICO", "BOLIVAR", "BOYACA", "CALDAS",
        "CAQUETA", "CASANARE", "CAUCA", "CESAR", "CHOCO", "CORDOBA", "CUNDINAMARCA",
        "GUAINIA", "GUAVIARE", "HUILA", "LA GUAJIRA", "MAGDALENA", "META", "NARIÑO",
        "NORTE DE SANTANDER", "PUTUMAYO", "QUINDIO", "RISARALDA", "SAN ANDRES", 
        "SANTANDER", "SUCRE", "TOLIMA", "VALLE DEL CAUCA", "VAUPES", "VICHADA", "BOGOTA D.C.", "NACIONAL"
    ]
    df_deptos = pd.DataFrame({
        'id_departamento': range(1, len(deptos) + 1),
        'nombre_departamento': deptos,
        'codigo_dane': [str(i).zfill(2) for i in range(1, len(deptos) + 1)]
    })
    df_deptos.to_sql('dim_departamento', engine, if_exists='replace', index=False)
    print("[OK] dim_departamento cargada.")

if __name__ == "__main__":
    engine = obtener_engine()
    cargar_dim_periodo(engine)
    cargar_predicciones_boletines(engine)
    cargar_dim_departamento(engine)
    print("\n=== TABLAS DE SOPORTE CARGADAS EXITOSAMENTE ===")
