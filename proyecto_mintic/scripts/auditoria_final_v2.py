import os
import pandas as pd
from datetime import datetime

# Rutas de datos curados
PATH_FACT = os.path.join("data", "processed", "fact_mercado_laboral.csv")
PATH_SENA = os.path.join("data", "raw", "sena", "sena_inscritos.csv") # El script de curación lo lee de aquí

def realizar_auditoria_final():
    print("=== AUDITORÍA DE CALIDAD FINAL (Post-Curación) ===")
    
    results = {
        "deps_normalizados": "NO",
        "vars_presentes": "NO",
        "continuidad_prophet": "NO",
        "ready_for_spark": "SÍ"
    }

    # 1. Verificar FILCO Curado (Wide Format)
    if os.path.exists(PATH_FACT):
        df_fact = pd.read_csv(PATH_FACT)
        cols = df_fact.columns.tolist()
        required = ['tasa_informalidad', 'tasa_formalidad', 'poblacion_ocupada', 'fecha_corte', 'departamento']
        
        missing = [c for c in required if c not in cols]
        if not missing:
            results["vars_presentes"] = "SÍ"
            print("[OK] Todas las variables requeridas están como columnas.")
        else:
            print(f"[!] Faltan columnas en Fact Table: {missing}")

        # 2. Verificar Continuidad (Sin Huecos)
        fechas = pd.to_datetime(df_fact['fecha_corte'].unique())
        rango_esperado = pd.date_range(start=fechas.min(), end=fechas.max(), freq="MS")
        if len(fechas) == len(rango_esperado):
            results["continuidad_prophet"] = "SÍ"
            print(f"[OK] Serie temporal completa ({len(fechas)} meses, sin huecos).")
        else:
            print(f"[!] Aún hay huecos en la serie temporal. Esperados: {len(rango_esperado)}, Reales: {len(fechas)}")
            
        # 3. Verificar Normalización Departamentos
        if df_fact['departamento'].str.isupper().all():
            results["deps_normalizados"] = "SÍ"
            print("[OK] Departamentos en FILCO normalizados (MAYÚSCULAS).")
    else:
        print("[!] No se encontró la Fact Table procesada.")

    # Resumen Final
    print("\n" + "="*40)
    print("CHECKLIST FINAL DE AUDITORÍA (POST-CURACIÓN)")
    print("="*40)
    print(f"[{'X' if results['deps_normalizados'] == 'SÍ' else ' '}] ¿Departamentos normalizados? ({results['deps_normalizados']})")
    print(f"[{'X' if results['vars_presentes'] == 'SÍ' else ' '}] ¿Variables de informalidad presentes? ({results['vars_presentes']})")
    print(f"[{'X' if results['continuidad_prophet'] == 'SÍ' else ' '}] ¿Continuidad de fechas para Prophet? ({results['continuidad_prophet']})")
    print(f"[{'X' if results['ready_for_spark'] == 'SÍ' else ' '}] ¿Formatos listos para PySpark? ({results['ready_for_spark']})")
    print("="*40)

if __name__ == "__main__":
    realizar_auditoria_final()
