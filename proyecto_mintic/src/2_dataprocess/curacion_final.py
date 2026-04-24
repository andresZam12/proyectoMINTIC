import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import unicodedata

# Cargar variables de entorno desde ambas posibles ubicaciones
load_dotenv() # .env en raíz
load_dotenv("proyecto_mintic/.env") # .env en subcarpeta si existe

# Configuración de Rutas
RAW_FILCO_DIR = os.path.join("data", "raw", "filco_csv")
RAW_SENA_PATH = os.path.join("data", "raw", "sena", "sena_inscritos.csv")

def normalizar_departamento(nombre):
    if not isinstance(nombre, str): return "NACIONAL"
    # Quitar tildes, a mayúsculas y limpiar espacios
    nombre = ''.join(c for c in unicodedata.normalize('NFD', nombre) if unicodedata.category(c) != 'Mn')
    return nombre.strip().upper()

def procesar_filco():
    print("[*] Procesando y Pivotando datos de FILCO...")
    all_files = [os.path.join(RAW_FILCO_DIR, f) for f in os.listdir(RAW_FILCO_DIR) if f.endswith('.csv')]
    
    df_list = []
    for f in all_files:
        df_list.append(pd.read_csv(f))
    
    df_long = pd.concat(df_list, ignore_index=True)
    
    # Asegurar que 'sexo' exista (si no, poner 'TOTAL')
    if 'sexo' not in df_long.columns:
        df_long['sexo'] = 'TOTAL'
        
    # Pivotar: De Largo a Ancho
    # Queremos: departamento, fecha_corte, sexo | tasa_informalidad, tasa_formalidad, poblacion_ocupada
    df_wide = df_long.pivot_table(
        index=['departamento', 'fecha_corte', 'sexo'],
        columns='variable',
        values='valor',
        aggfunc='first'
    ).reset_index()
    
    # Normalizar nombres de columnas resultantes del pivot
    df_wide.columns.name = None
    
    # Asegurar que las columnas críticas existan (aunque sea con NaNs)
    for col in ['tasa_informalidad', 'tasa_formalidad', 'poblacion_ocupada']:
        if col not in df_wide.columns:
            df_wide[col] = np.nan
            
    # Normalizar Departamentos
    df_wide['departamento'] = df_wide['departamento'].apply(normalizar_departamento)
    
    # Convertir fecha
    df_wide['fecha_corte'] = pd.to_datetime(df_wide['fecha_corte'])
    
    # IMPUTACIÓN PARA PROPHET: Rellenar huecos temporales
    print("[*] Aplicando imputación lineal para series temporales...")
    df_final = []
    for (dep, sex), group in df_wide.groupby(['departamento', 'sexo']):
        # Reindexar para asegurar continuidad mensual
        group = group.set_index('fecha_corte').resample('MS').asfreq()
        # Interpolar linealmente
        group[['tasa_informalidad', 'tasa_formalidad', 'poblacion_ocupada']] = group[['tasa_informalidad', 'tasa_formalidad', 'poblacion_ocupada']].interpolate(method='linear')
        group['departamento'] = dep
        group['sexo'] = sex
        df_final.append(group.reset_index())
        
    return pd.concat(df_final, ignore_index=True)

def procesar_sena():
    print("[*] Normalizando datos del SENA...")
    if not os.path.exists(RAW_SENA_PATH):
        print("[!] Archivo SENA no encontrado.")
        return pd.DataFrame()
        
    df_sena = pd.read_csv(RAW_SENA_PATH)
    
    # Renombrar columnas según estándar
    df_sena = df_sena.rename(columns={
        'nombre_de_la_ocupaci_n': 'oficio',
        'n_mero_de_inscritos_2020': 'inscritos'
    })
    
    # Asegurar departamento
    if 'departamento' not in df_sena.columns:
        df_sena['departamento'] = 'NACIONAL'
    else:
        df_sena['departamento'] = df_sena['departamento'].apply(normalizar_departamento)
        
    # Asegurar vacantes (si no existe, poner 0 o promedio)
    if 'vacantes' not in df_sena.columns:
        df_sena['vacantes'] = 0
        
    return df_sena

def cargar_a_postgres(df):
    print("[*] Cargando datos a PostgreSQL (Docker)...")
    try:
        user = os.getenv("POSTGRES_USER", "mintic_user")
        pwd = os.getenv("POSTGRES_PASSWORD", "mintic2026")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "mintic_db")
        
        engine = create_engine(f'postgresql://{user}:{pwd}@{host}:{port}/{db}')
        
        # Guardar en tabla fact_mercado_laboral
        df.to_sql('fact_mercado_laboral', engine, if_exists='replace', index=False)
        print("[SUCCESS] Datos cargados exitosamente en la tabla 'fact_mercado_laboral'.")
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a la base de datos: {e}")

def main():
    print("=== INICIANDO CURACIÓN Y UNIFICACIÓN FINAL ===")
    
    df_filco = procesar_filco()
    df_sena = procesar_sena()
    
    # Unificación: En este caso, para Power BI, a veces es mejor subirlas como tablas separadas
    # o unirlas por departamento/fecha. Dado que SENA es anual y FILCO es mensual, 
    # las subiremos como una tabla maestra unificada si el usuario lo requiere, 
    # o simplemente aseguramos que ambas estén en la DB.
    
    # Guardar localmente para auditoría antes de subir
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    df_filco.to_csv(os.path.join("data", "processed", "fact_mercado_laboral.csv"), index=False)
    
    # Por ahora, cargaremos la de FILCO que es la "Fact Table" principal para Prophet
    cargar_a_postgres(df_filco)
    
    # También cargamos SENA para cruces en Power BI
    if not df_sena.empty:
        try:
            user = os.getenv("POSTGRES_USER", "mintic_user")
            pwd = os.getenv("POSTGRES_PASSWORD", "mintic2026")
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            db = os.getenv("POSTGRES_DB", "mintic_db")
            engine = create_engine(f'postgresql://{user}:{pwd}@{host}:{port}/{db}')
            df_sena.to_sql('dim_sena_empleabilidad', engine, if_exists='replace', index=False)
            print("[SUCCESS] Datos del SENA cargados en 'dim_sena_empleabilidad'.")
        except: pass

    print("\n=== RESUMEN DE CURACIÓN ===")
    print(f"Registros FILCO (Interpolados): {len(df_filco)}")
    print(f"Registros SENA: {len(df_sena)}")
    print("============================")

if __name__ == "__main__":
    main()
