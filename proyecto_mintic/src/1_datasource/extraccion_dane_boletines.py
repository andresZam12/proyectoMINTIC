import requests
import os
import time
from datetime import datetime

RUTA_SALIDA = os.path.join("data", "raw", "dane_boletines")

MESES = ["ene","feb","mar","abr","may","jun",
         "jul","ago","sep","oct","nov","dic"]

ANIOS = [2022, 2023, 2024, 2025, 2026]

LIMITE_MES = {"2026": ["ene", "feb"]}

BASE_URL = "https://www.dane.gov.co/files/operaciones/GEIH/bol-GEIH-{mes}{anio}.pdf"


def extraer_boletines():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando descarga boletines DANE...\n")
    os.makedirs(RUTA_SALIDA, exist_ok=True)

    descargados = omitidos = errores = 0

    for anio in ANIOS:
        for mes in LIMITE_MES.get(str(anio), MESES):
            url      = BASE_URL.format(mes=mes, anio=anio)
            nombre   = f"bol-GEIH-{mes}{anio}.pdf"
            ruta_pdf = os.path.join(RUTA_SALIDA, nombre)

            if os.path.exists(ruta_pdf):
                print(f"  ⏭ Ya existe: {nombre}")
                omitidos += 1
                continue

            try:
                r = requests.get(url, timeout=30, stream=True)
                if r.status_code == 200:
                    with open(ruta_pdf, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"  ✓ {nombre}  ({os.path.getsize(ruta_pdf)/1024:.0f} KB)")
                    descargados += 1
                else:
                    print(f"  ✗ {nombre}  → HTTP {r.status_code}")
                    errores += 1
                time.sleep(0.5)
            except Exception as e:
                print(f"  ✗ {nombre}  → {e}")
                errores += 1

    print(f"\n{'─'*50}")
    print(f"  ✓ Descargados : {descargados}")
    print(f"  ⏭ Omitidos    : {omitidos}")
    print(f"  ✗ Errores     : {errores}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Descarga completada.")


if __name__ == "__main__":
    extraer_boletines()
