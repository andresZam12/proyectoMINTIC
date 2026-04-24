import os
import pandas as pd
import re
import unicodedata
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas
RAW_PATH = os.path.join("data", "raw", "filco")
CLEAN_PATH = os.path.join("data", "raw", "filco_csv")

MESES_MAP = {
    'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06',
    'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
}

def asegurar_directorios():
    if not os.path.exists(CLEAN_PATH):
        os.makedirs(CLEAN_PATH)

def normalizar_texto(texto):
    """
    Normaliza el texto para PySpark: sin tildes, minúsculas y snake_case.
    POR QUÉ: PySpark y las bases de datos de Big Data (Hive/Presto) prefieren 
    nombres de columnas sin caracteres especiales para evitar errores de sintaxis en SQL.
    """
    if not isinstance(texto, str):
        texto = str(texto)
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = texto.lower().strip()
    texto = re.sub(r'[^a-z0-9_]', '_', texto)
    texto = re.sub(r'_+', '_', texto).strip('_')
    return texto

def extraer_fecha(nombre_archivo):
    """
    Extrae la fecha de corte del nombre del archivo DANE.
    POR QUÉ: Para modelos de series de tiempo como Prophet, necesitamos una columna 
    temporal clara (fecha_corte) que identifique cuándo se recolectó el dato.
    """
    anios = re.findall(r'202[2-6]', nombre_archivo)
    meses_encontrados = []
    for mes_abr in MESES_MAP.keys():
        if mes_abr in nombre_archivo.lower():
            meses_encontrados.append(mes_abr)
    
    if anios:
        anio = anios[-1]
        mes = MESES_MAP.get(meses_encontrados[-1], '01') if meses_encontrados else '01'
        return f"{anio}-{mes}-01"
    return "1900-01-01"

def limpiar_excel_pro(ruta_archivo):
    """
    Limpieza robusta para archivos DANE.
    POR QUÉ: Los archivos del DANE contienen metadatos (logos, notas) que no son datos.
    Esta función filtra esos ruidos y extrae solo las métricas de informalidad.
    """
    try:
        xls = pd.ExcelFile(ruta_archivo)
        
        # Seleccionar hoja de 'Total nacional' o similar
        target_sheet = next((s for s in xls.sheet_names if 'total nacional' in s.lower()), None)
        if not target_sheet:
            target_sheet = next((s for s in xls.sheet_names if 'prop informalidad' in s.lower()), xls.sheet_names[0])

        df_raw = pd.read_excel(ruta_archivo, sheet_name=target_sheet, header=None)
        
        # Eliminar columnas que son 100% nulas
        df_raw = df_raw.dropna(axis=1, how='all')
        
        fecha_corte = extraer_fecha(os.path.basename(ruta_archivo))
        result_data = []

        for _, row in df_raw.iterrows():
            # Convertir fila a lista limpia de nulos
            clean_row = [v for v in row.values if pd.notnull(v)]
            if not clean_row: continue

            # Buscar filas con palabras clave
            row_text = " ".join([str(v).lower() for v in clean_row])
            keywords = ['formal', 'informal', 'total nacional', 'proporcion']
            
            if any(kw in row_text for kw in keywords):
                # Intentar identificar categoría (primer string largo) y valor (último número)
                str_vals = [str(v) for v in clean_row if isinstance(v, str) and len(str(v)) > 3]
                num_vals = [v for v in clean_row if isinstance(v, (int, float))]
                
                if str_vals and num_vals:
                    categoria = normalizar_texto(str_vals[0])
                    # Estandarización de nombres críticos
                    if 'informal' in categoria: categoria = 'tasa_informalidad'
                    elif 'formal' in categoria: categoria = 'tasa_formalidad'
                    
                    result_data.append({
                        'departamento': 'nacional',
                        'variable': categoria,
                        'valor': num_vals[-1],
                        'fecha_corte': fecha_corte
                    })
        
        if not result_data:
            return None, "No se detectaron datos numéricos con categorías válidas"

        return pd.DataFrame(result_data), None
    except Exception as e:
        return None, str(e)

def main():
    print("=== Iniciando Limpieza Robusta (MinTIC 2026) ===")
    asegurar_directorios()
    archivos = [f for f in os.listdir(RAW_PATH) if f.endswith(('.xls', '.xlsx'))]
    
    total_registros = 0
    reporte = []
    
    for nombre in archivos:
        df, error = limpiar_excel_pro(os.path.join(RAW_PATH, nombre))
        if df is not None:
            nombre_csv = nombre.rsplit('.', 1)[0] + ".csv"
            df.to_csv(os.path.join(CLEAN_PATH, nombre_csv), index=False)
            total_registros += len(df)
            reporte.append(f"[OK] {nombre} -> {len(df)} registros")
        else:
            reporte.append(f"[FAIL] {nombre}: {error}")
            
    print("\n".join(reporte))
    print(f"\nProceso finalizado. Total registros: {total_registros}")
    print(f"Archivos limpios en: {CLEAN_PATH}")

if __name__ == "__main__":
    main()
