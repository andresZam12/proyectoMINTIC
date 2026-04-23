import requests
import pandas as pd
import os
import time
from datetime import datetime

# ── Configuración ────────────────────────────────────────────────
URL_API = "https://www.datos.gov.co/resource/8pqf-rmzr.json"
RUTA_SALIDA  = os.path.join("data", "raw", "sena", "sena_inscritos.csv")
LIMITE       = 10000   # lotes más pequeños para no saturar la API
MAX_REGISTROS = 10000 # límite razonable para el proyecto
MAX_REINTENTOS = 3
PAUSA_ENTRE_LOTES = 1  # segundos entre llamadas

def llamar_api(offset, reintento=0):
    """Llama la API con reintentos automáticos."""
    try:
        params = {"$limit": LIMITE, "$offset": offset, "$order": ":id"}
        r = requests.get(URL_API, params=params, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        if reintento < MAX_REINTENTOS:
            espera = (reintento + 1) * 5
            print(f"  ⚠ Error en offset {offset}, reintentando en {espera}s... ({e})")
            time.sleep(espera)
            return llamar_api(offset, reintento + 1)
        else:
            print(f"  ✗ Falló después de {MAX_REINTENTOS} reintentos: {e}")
            return None

def extraer_sena():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extracción SENA...")
    print(f"  URL: {URL_API}")
    print(f"  Límite máximo: {MAX_REGISTROS:,} registros\n")

    todos = []
    offset = 0
    lote   = 1

    while len(todos) < MAX_REGISTROS:
        print(f"  Lote {lote:02d} | offset {offset:,} → ", end="", flush=True)

        datos = llamar_api(offset)

        # Sin datos → fin de la paginación
        if not datos:
            print("fin del dataset.")
            break

        todos.extend(datos)
        print(f"{len(todos):,} registros acumulados")

        offset += LIMITE
        lote   += 1
        time.sleep(PAUSA_ENTRE_LOTES)

    if not todos:
        print("\n✗ No se obtuvieron datos.")
        return

    # ── Construir DataFrame ──────────────────────────────────────
    df = pd.DataFrame(todos)

    print(f"\n{'─'*55}")
    print(f"  Total registros : {len(df):,}")
    print(f"  Total columnas  : {len(df.columns)}")
    print(f"  Columnas        : {list(df.columns)}")
    print(f"  Nulos por columna:\n{df.isnull().sum().to_string()}")
    print(f"{'─'*55}")
    print(f"\n  Muestra (3 filas):")
    print(df.head(3).to_string())

    # ── Guardar ──────────────────────────────────────────────────
    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8-sig")

    tam_kb = os.path.getsize(RUTA_SALIDA) / 1024
    print(f"\n  ✓ Guardado en : {RUTA_SALIDA}")
    print(f"  ✓ Tamaño      : {tam_kb:.1f} KB")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Extracción SENA completada.")

if __name__ == "__main__":
    extraer_sena()