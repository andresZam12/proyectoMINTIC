import os
import subprocess
import sys
from datetime import datetime

def run_script(script_path):
    print(f"\n{'='*60}")
    print(f"[*] EJECUTANDO: {script_path}")
    print(f"{'='*60}")
    
    # Obtener el directorio base para asegurar que Python encuentra el path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, script_path)
    
    if not os.path.exists(full_path):
        print(f"[ERROR] ERROR: El archivo {full_path} no existe.")
        return False
        
    try:
        # Ejecutar el script usando el ejecutable actual de Python
        result = subprocess.run([sys.executable, full_path], check=True, text=True)
        print(f"[SUCCESS] FINALIZADO CON ÉXITO: {script_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] ERROR durante la ejecución de {script_path}")
        print(f"Código de salida: {e.returncode}")
        return False

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] INICIANDO ORQUESTADOR (PIPELINE AUTOMÁTICO)")
    print("Este script ejecutará secuencialmente la extracción y curación de datos.\n")
    
    # Definir el orden estricto de ejecución
    pipeline = [
        "src/1_datasource/extraccion_geih.py",
        "src/1_datasource/extraccion_filco.py",
        "src/1_datasource/extraccion_sena.py",
        "src/2_dataprocess/curacion_final.py"
    ]
    
    for script in pipeline:
        success = run_script(script)
        if not success:
            print("\n[STOP] PIPELINE DETENIDO debido a un error en el paso anterior.")
            sys.exit(1)
            
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [SUCCESS] PIPELINE COMPLETADO EXITOSAMENTE.")
    print("Los datos están listos en PostgreSQL y en la carpeta 'data/processed' para ser consumidos por Power BI.")

if __name__ == "__main__":
    main()
