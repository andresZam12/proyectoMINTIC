import subprocess
import sys
import os

def run_script(script_path):
    print("\n" + "="*50)
    print(f"EJECUTANDO: {script_path}")
    print("="*50)
    try:
        # Ejecutamos el script y mostramos la salida en tiempo real
        result = subprocess.run([sys.executable, script_path], check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] El script {script_path} falló.")
        return False
    except FileNotFoundError:
        print(f"\n[ERROR] No se encontró el archivo: {script_path}")
        return False

def main():
    print("=== PIPELINE AUTOMÁTICO - PROYECTO MINTIC 2026 ===")
    
    # 1. Extracción
    scripts = [
        "proyecto_mintic/src/1_datasource/extraccion_geih.py",
        "proyecto_mintic/src/1_datasource/extraccion_filco.py",
        "proyecto_mintic/src/1_datasource/extraccion_sena.py",
        "proyecto_mintic/src/2_dataprocess/curacion_final.py",
        "proyecto_mintic/src/4_dataproduct/modelo_prophet.py"
    ]

    for script in scripts:
        if not run_script(script):
            print(f"\n[ABORTANDO] Fallo crítico en {script}")
            sys.exit(1)

    print("\n" + "!"*50)
    print("¡TODO LISTO! Datos cargados y modelo entrenado.")
    print("Ahora puedes actualizar Power BI.")
    print("!"*50)

if __name__ == "__main__":
    main()