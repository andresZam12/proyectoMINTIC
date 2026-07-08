import os
import json
import hashlib
from datetime import datetime
import pandas as pd

RUTA_RAW      = os.path.join("data", "raw")
RUTA_METADATA = os.path.join(RUTA_RAW, "metadata.json")

ESQUEMA_SENA = [
    "nombre_de_la_ocupaci_n",
    "n_mero_de_inscritos_2019",
    "n_mero_de_inscritos_2020",
]

EXTENSIONES_VALIDAS = {
    "sena":           [".csv"],
    "dane_boletines": [".pdf"],
    "geih":           [".zip", ".csv", ".sav", ".dta"],
    "filco":          [".xlsx", ".csv", ".xls"],
}


def md5_archivo(ruta):
    h = hashlib.md5()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def tam_legible(bytes_):
    for unidad in ["B", "KB", "MB", "GB"]:
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unidad}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


def listar_archivos(ruta_carpeta, extensiones):
    if not os.path.exists(ruta_carpeta):
        return []
    return [
        os.path.join(ruta_carpeta, nombre)
        for nombre in sorted(os.listdir(ruta_carpeta))
        if os.path.splitext(nombre.lower())[1] in extensiones
    ]


def info_archivo(ruta):
    stat = os.stat(ruta)
    return {
        "nombre":     os.path.basename(ruta),
        "tamanio":    tam_legible(stat.st_size),
        "bytes":      stat.st_size,
        "modificado": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        "md5":        md5_archivo(ruta),
    }


def validar_sena():
    ruta = os.path.join(RUTA_RAW, "sena", "sena_inscritos.csv")
    resultado = {"fuente": "SENA", "estado": "ERROR", "archivos": [], "alertas": []}

    if not os.path.exists(ruta):
        resultado["alertas"].append("Archivo no encontrado: sena_inscritos.csv")
        return resultado

    try:
        df = pd.read_csv(ruta, encoding="utf-8-sig")
        resultado["archivos"].append(info_archivo(ruta))
        resultado["registros"]  = len(df)
        resultado["columnas"]   = list(df.columns)
        resultado["nulos"]      = df.isnull().sum().to_dict()
        resultado["duplicados"] = int(df.duplicated().sum())

        cols_lower = [c.lower() for c in df.columns]
        faltantes  = [c for c in ESQUEMA_SENA if c not in cols_lower]
        if faltantes:
            resultado["alertas"].append(f"Columnas faltantes: {faltantes}")

        if df.isnull().values.any():
            pct_nulos = df.isnull().mean().max() * 100
            if pct_nulos > 20:
                resultado["alertas"].append(f"Columna con más del {pct_nulos:.0f}% de nulos")

        resultado["estado"] = "OK" if not resultado["alertas"] else "ADVERTENCIA"
        print(f"  [SENA]  {len(df):,} registros · {len(df.columns)} cols · {resultado['estado']}")
    except Exception as e:
        resultado["alertas"].append(str(e))

    return resultado


def validar_dane_boletines():
    ruta_carpeta = os.path.join(RUTA_RAW, "dane_boletines")
    resultado    = {"fuente": "DANE_boletines", "estado": "ERROR", "archivos": [], "alertas": []}

    archivos = listar_archivos(ruta_carpeta, [".pdf"])
    if not archivos:
        resultado["alertas"].append("No se encontraron PDFs en dane_boletines/")
        return resultado

    total_bytes = 0
    for ruta in archivos:
        info = info_archivo(ruta)
        resultado["archivos"].append(info)
        total_bytes += info["bytes"]
        if info["bytes"] < 50_000:
            resultado["alertas"].append(f"PDF sospechosamente pequeño: {info['nombre']}")

    resultado["total_archivos"] = len(archivos)
    resultado["tamanio_total"]  = tam_legible(total_bytes)
    resultado["estado"] = "OK" if not resultado["alertas"] else "ADVERTENCIA"
    print(f"  [DANE]  {len(archivos)} PDFs · {tam_legible(total_bytes)} · {resultado['estado']}")
    return resultado


def validar_geih():
    resultado   = {"fuente": "GEIH", "estado": "PENDIENTE", "archivos": [], "alertas": []}
    encontrados = 0

    for anio in ["2024", "2025"]:
        ruta_anio = os.path.join(RUTA_RAW, "geih", anio)
        archivos  = listar_archivos(ruta_anio, [".zip", ".csv", ".sav", ".dta"])
        if archivos:
            resultado["archivos"].extend(info_archivo(r) for r in archivos)
            encontrados += len(archivos)
        else:
            resultado["alertas"].append(f"Sin archivos en geih/{anio}/ — ejecutar extraccion_geih.py")

    if encontrados > 0:
        resultado["estado"] = "OK" if not resultado["alertas"] else "PARCIAL"
    print(f"  [GEIH]  {encontrados} archivo(s) · {resultado['estado']}")
    return resultado


def validar_filco():
    ruta_carpeta = os.path.join(RUTA_RAW, "filco")
    resultado    = {"fuente": "FILCO", "estado": "PENDIENTE", "archivos": [], "alertas": []}

    archivos = listar_archivos(ruta_carpeta, [".xlsx", ".csv", ".xls"])
    if not archivos:
        resultado["alertas"].append("Sin archivos en filco/ — ejecutar extraccion_filco.py")
        print("  [FILCO] sin archivos · PENDIENTE")
        return resultado

    total_bytes = 0
    for ruta in archivos:
        try:
            info = info_archivo(ruta)
            resultado["archivos"].append(info)
            total_bytes += info["bytes"]
            if ruta.endswith((".xlsx", ".xls")):
                df = pd.read_excel(ruta, nrows=5)
            else:
                df = pd.read_csv(ruta, nrows=5)
            resultado.setdefault("muestras", {})[info["nombre"]] = list(df.columns)
        except Exception as e:
            resultado["alertas"].append(f"{os.path.basename(ruta)}: {e}")

    resultado["total_archivos"] = len(archivos)
    resultado["tamanio_total"]  = tam_legible(total_bytes)
    resultado["estado"] = "OK" if not resultado["alertas"] else "ADVERTENCIA"
    print(f"  [FILCO] {len(archivos)} archivo(s) · {tam_legible(total_bytes)} · {resultado['estado']}")
    return resultado


def resumen_data_lake(validaciones):
    estados = [v["estado"] for v in validaciones]
    return {
        "total_fuentes": len(validaciones),
        "ok":            estados.count("OK"),
        "advertencia":   estados.count("ADVERTENCIA"),
        "parcial":       estados.count("PARCIAL"),
        "pendiente":     estados.count("PENDIENTE"),
        "error":         estados.count("ERROR"),
        "listo_para_f3": all(e in ("OK", "ADVERTENCIA", "PARCIAL") for e in estados if e != "PENDIENTE"),
    }


def validar_datos():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando validación del Data Lake...\n")

    validaciones = [validar_sena(), validar_dane_boletines(), validar_geih(), validar_filco()]
    resumen = resumen_data_lake(validaciones)

    metadata = {
        "generado_en": datetime.now().isoformat(),
        "ruta_raw":    os.path.abspath(RUTA_RAW),
        "resumen":     resumen,
        "fuentes":     validaciones,
    }

    os.makedirs(RUTA_RAW, exist_ok=True)
    with open(RUTA_METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n{'─'*55}")
    print(f"  OK          : {resumen['ok']}")
    print(f"  Advertencia : {resumen['advertencia']}")
    print(f"  Pendiente   : {resumen['pendiente']}")
    print(f"  Listo F3    : {'Sí' if resumen['listo_para_f3'] else 'No'}")
    print(f"  Metadata    : {RUTA_METADATA}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Validación completada.")


if __name__ == "__main__":
    validar_datos()
