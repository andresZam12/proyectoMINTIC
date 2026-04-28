import requests
import pandas as pd
import os
import time
from datetime import datetime

# Configuración
URL_API = "https://www.datos.gov.co/resource/8pqf-rmzr.json"
RUTA_SALIDA = os.path.join("data", "raw", "sena", "sena_inscritos.csv")
LIMITE = 10000
MAX_REGISTROS = 50000 
MAX_REINTENTOS = 3
PAUSA_ENTRE_LOTES = 1

def llamar_api(offset, reintento=0):
    try:
        params = {"$limit": LIMITE, "$offset": offset, "$order": ":id"}
        r = requests.get(URL_API, params=params, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        if reintento < MAX_REINTENTOS:
            espera = (reintento + 1) * 5
            print(f"  [WARNING] Error en offset {offset}, reintentando en {espera}s... ({e})")
            time.sleep(espera)
            return llamar_api(offset, reintento + 1)
        else:
            print(f"  [ERROR] Falló después de {MAX_REINTENTOS} reintentos: {e}")
            return None

def extraer_sena():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extracción SENA...")
    
    todos = []
    offset = 0
    lote = 1

    while len(todos) < MAX_REGISTROS:
        # Usamos -> en lugar de la flecha especial para evitar errores de consola
        print(f"  Lote {lote:02d} | offset {offset:,} -> ", end="", flush=True)
        datos = llamar_api(offset)
        if not datos:
            print("fin del dataset o error.")
            break

        todos.extend(datos)
        print(f"{len(todos):,} registros acumulados")
        
        if len(datos) < LIMITE:
            break

        offset += LIMITE
        lote += 1
        time.sleep(PAUSA_ENTRE_LOTES)

    if not todos:
        print("\n[ERROR] No se obtuvieron datos.")
        return

    df = pd.DataFrame(todos)
    
    if 'vacantes' not in df.columns and 'n_mero_de_inscritos_2020' in df.columns:
        df['vacantes_estimadas'] = pd.to_numeric(df['n_mero_de_inscritos_2020'], errors='coerce').fillna(0) * 0.1
        df['vacantes_estimadas'] = df['vacantes_estimadas'].astype(int)

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8-sig")
    print(f"\n  [SUCCESS] Guardado en: {RUTA_SALIDA}")

if __name__ == "__main__":
    extraer_sena()