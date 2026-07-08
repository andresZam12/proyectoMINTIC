import requests
import pandas as pd
import os
import time
from datetime import datetime

URL_API       = "https://www.datos.gov.co/resource/8pqf-rmzr.json"
RUTA_SALIDA   = os.path.join("data", "raw", "sena", "sena_inscritos.csv")
LIMITE        = 10000
MAX_REGISTROS = 10000
MAX_REINTENTOS = 3
PAUSA         = 1


def llamar_api(offset, reintento=0):
    try:
        r = requests.get(URL_API, params={"$limit": LIMITE, "$offset": offset, "$order": ":id"}, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        if reintento < MAX_REINTENTOS:
            time.sleep((reintento + 1) * 5)
            return llamar_api(offset, reintento + 1)
        print(f"  ✗ Falló después de {MAX_REINTENTOS} reintentos: {e}")
        return None


def extraer_sena():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extracción SENA...")

    todos, offset, lote = [], 0, 1

    while len(todos) < MAX_REGISTROS:
        print(f"  Lote {lote:02d} | offset {offset:,} → ", end="", flush=True)
        datos = llamar_api(offset)
        if not datos:
            print("fin del dataset.")
            break
        todos.extend(datos)
        print(f"{len(todos):,} registros acumulados")
        offset += LIMITE
        lote   += 1
        time.sleep(PAUSA)

    if not todos:
        print("✗ No se obtuvieron datos.")
        return

    df = pd.DataFrame(todos)
    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8-sig")

    print(f"\n  ✓ {len(df):,} registros guardados en {RUTA_SALIDA}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Extracción SENA completada.")


if __name__ == "__main__":
    extraer_sena()
