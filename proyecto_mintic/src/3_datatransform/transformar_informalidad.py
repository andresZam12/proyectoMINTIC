"""
transformar_informalidad.py
Lee los anexos GEIH-EISS del DANE (informalidad laboral) y los carga a PostgreSQL.
Usa solo el archivo más reciente que ya contiene la serie completa 2021-2026.
"""
import sys
import os
import re
import warnings
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")
load_dotenv()

# ── Configuración ─────────────────────────────────────────────────
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB   = os.getenv("POSTGRES_DB",   "mintic_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "mintic_user")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "mintic2026")

RUTA_FILCO = os.path.join("data", "raw", "filco", "Data")
# Archivo con la serie completa 2021-2026
ARCHIVO_PRINCIPAL = "anex-GEIHEISS-dic2025-feb2026.xlsx"

# Mapeo trimestre → (mes_central, offset_año)
# offset_año=0 → mismo año del header; offset_año=1 → año siguiente
TRIMESTRE_MES = {
    "ene": (2, 0),
    "feb": (3, 0),
    "mar": (4, 0),
    "abr": (5, 0),
    "may": (6, 0),
    "jun": (7, 0),
    "jul": (8, 0),
    "ago": (9, 0),
    "sep": (10, 0),
    "oct": (11, 0),
    "nov": (12, 0),  # Nov-ene → diciembre del año de inicio
    "dic": (1, 1),   # Dic-feb → enero del año siguiente
}


def conectar():
    return psycopg2.connect(
        host=POSTGRES_HOST, port=POSTGRES_PORT, dbname=POSTGRES_DB,
        user=POSTGRES_USER, password=POSTGRES_PASS,
    )


def crear_tabla(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fact_informalidad (
                id                SERIAL PRIMARY KEY,
                id_periodo        INTEGER REFERENCES dim_periodo(id_periodo),
                ciudad            VARCHAR(120),
                sexo              VARCHAR(20) DEFAULT 'Total',
                tasa_informalidad NUMERIC(6,2),
                ocupados_total    NUMERIC(10,1),
                ocupados_formal   NUMERIC(10,1),
                ocupados_informal NUMERIC(10,1),
                fuente            VARCHAR(30) DEFAULT 'DANE_GEIH_EISS',
                fecha_carga       TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_informalidad_periodo
                ON fact_informalidad(id_periodo);
        """)
    conn.commit()
    print("  ✓ Tabla fact_informalidad lista")


def leer_dim_periodo(conn) -> dict:
    """Retorna {(anio, mes): id_periodo}"""
    with conn.cursor() as cur:
        cur.execute("SELECT id_periodo, anio, mes FROM dim_periodo")
        return {(r[1], r[2]): r[0] for r in cur.fetchall()}


def construir_columnas(df_raw) -> list:
    """
    Reconstruye la lista [(año, mes), ...] para cada columna de datos (cols 1..60).
    Para trimestres con año explícito en el label (ej 'Nov 21 - ene 22'),
    extrae el año directamente del texto en lugar del header de la fila.
    """
    row_anio = list(df_raw.iloc[10])
    row_trim = list(df_raw.iloc[11])

    anio_header = None
    columnas = []
    for i in range(1, len(row_anio)):
        if pd.notna(row_anio[i]):
            try:
                anio_header = int(row_anio[i])
            except (ValueError, TypeError):
                pass

        trim_label = str(row_trim[i]).strip().lower() if i < len(row_trim) and pd.notna(row_trim[i]) else ""
        primer_mes = trim_label[:3]
        mes, offset = TRIMESTRE_MES.get(primer_mes, (None, None))

        if mes is None:
            columnas.append((None, None))
            continue

        # Si el label tiene años explícitos (ej "nov 21 - ene 22"), usar el primer año
        numeros = re.findall(r"\b(\d{2})\b", trim_label)
        if numeros:
            anio_inicio = 2000 + int(numeros[0])
        else:
            anio_inicio = anio_header

        if anio_inicio:
            columnas.append((anio_inicio + (offset or 0), mes))
        else:
            columnas.append((None, None))
    return columnas


def parsear_prop_informalidad(ruta: str, dim_periodo: dict) -> list:
    """
    Extrae la tasa de informalidad por ciudad/periodo.
    Retorna lista de tuplas para insertar en fact_informalidad.
    """
    df = pd.read_excel(ruta, sheet_name="Prop informalidad", header=None)
    columnas = construir_columnas(df)

    filas = []
    # Datos empiezan en fila 12
    for i in range(12, len(df)):
        row = list(df.iloc[i])
        ciudad = str(row[0]).strip() if pd.notna(row[0]) else None
        if not ciudad or ciudad == "nan":
            continue
        # Solo Total nacional y principales ciudades (sin AM repetidas)
        for j, (anio, mes) in enumerate(columnas):
            if anio is None or mes is None:
                continue
            id_periodo = dim_periodo.get((anio, mes))
            if id_periodo is None:
                continue
            val = row[j + 1] if (j + 1) < len(row) else None
            try:
                tasa = round(float(val), 2) if val is not None and str(val) != "nan" else None
            except (ValueError, TypeError):
                tasa = None
            if tasa is None:
                continue
            filas.append((id_periodo, ciudad, "Total", tasa, None, None, None))
    return filas


def parsear_sexo(ruta: str, dim_periodo: dict) -> list:
    """
    Extrae ocupados total/formal/informal por sexo a nivel nacional.
    """
    df = pd.read_excel(ruta, sheet_name="Sexo", header=None)
    columnas = construir_columnas(df)

    filas = []
    i = 13  # Datos inician en fila 13 (Población ocupada total)
    while i < len(df):
        row = list(df.iloc[i])
        concepto = str(row[0]).strip() if pd.notna(row[0]) else ""

        # Detectar bloque por sexo
        if concepto in ("Población ocupada", "Poblaci��nuevo ocupada"):
            pass

        # Procesar bloques de Hombres y Mujeres
        if concepto in ("Hombres", "Mujeres"):
            sexo = concepto
            # Siguiente fila = Formal, la de después = Informal
            row_formal   = list(df.iloc[i + 1]) if i + 1 < len(df) else []
            row_informal = list(df.iloc[i + 2]) if i + 2 < len(df) else []

            for j, (anio, mes) in enumerate(columnas):
                if anio is None or mes is None:
                    continue
                id_periodo = dim_periodo.get((anio, mes))
                if id_periodo is None:
                    continue
                def _v(r, idx):
                    try:
                        return round(float(r[idx + 1]), 1) if (idx + 1) < len(r) and str(r[idx + 1]) != "nan" else None
                    except (ValueError, TypeError):
                        return None
                formal   = _v(row_formal,   j)
                informal = _v(row_informal, j)
                total    = round(formal + informal, 1) if formal and informal else None

                if total is None:
                    continue
                filas.append((id_periodo, "Total nacional", sexo, None, total, formal, informal))
        i += 1
    return filas


def cargar(conn, filas: list, tabla: str = "fact_informalidad"):
    if not filas:
        print(f"  ⚠ Sin filas para {tabla}")
        return
    sql = f"""
        INSERT INTO {tabla}
            (id_periodo, ciudad, sexo, tasa_informalidad,
             ocupados_total, ocupados_formal, ocupados_informal)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, filas)
    conn.commit()
    print(f"  ✓ {tabla} — {len(filas):,} filas insertadas")


def main():
    ruta = os.path.join(RUTA_FILCO, ARCHIVO_PRINCIPAL)
    if not os.path.exists(ruta):
        print(f"✗ No se encontró: {ruta}")
        return

    print(f"Conectando a PostgreSQL ({POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB})...")
    conn = conectar()

    print("\n── Creando tabla ──────────────────────────────────────────")
    crear_tabla(conn)

    print("\n── Leyendo dim_periodo ────────────────────────────────────")
    dim_periodo = leer_dim_periodo(conn)
    print(f"  {len(dim_periodo)} periodos disponibles")

    print("\n── Prop informalidad por ciudad ───────────────────────────")
    filas_inf = parsear_prop_informalidad(ruta, dim_periodo)
    print(f"  Filas extraídas: {len(filas_inf):,}")
    cargar(conn, filas_inf)

    print("\n── Ocupados por sexo (nacional) ───────────────────────────")
    filas_sexo = parsear_sexo(ruta, dim_periodo)
    print(f"  Filas extraídas: {len(filas_sexo):,}")
    cargar(conn, filas_sexo)

    # Resumen
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), MIN(id_periodo), MAX(id_periodo) FROM fact_informalidad")
        total, p_min, p_max = cur.fetchone()
    print(f"\n  Total en fact_informalidad: {total:,} filas")

    conn.close()
    print("\n✓ Transformación FILCO completada.")


if __name__ == "__main__":
    main()
