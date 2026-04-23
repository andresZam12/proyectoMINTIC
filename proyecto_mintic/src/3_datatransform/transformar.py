"""
transformar.py  —  F3 · DataTransform
Lee el Data Lake (data/raw/), limpia con PySpark y carga a PostgreSQL via JDBC.
Ejecutar dentro del contenedor mintic_jupyter:
    spark-submit transformar.py
  o desde Jupyter con %run src/3_datatransform/transformar.py
"""

import os
from datetime import datetime, date
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    FloatType, DateType, TimestampType,
)

load_dotenv()

# ── Configuración ─────────────────────────────────────────────────
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")  # nombre del servicio Docker
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB   = os.getenv("POSTGRES_DB",   "mintic_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "mintic_user")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "mintic2026")

JDBC_URL = (
    f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    "?characterEncoding=UTF-8"
)
JDBC_PROPS = {
    "user":     POSTGRES_USER,
    "password": POSTGRES_PASS,
    "driver":   "org.postgresql.Driver",
}

RUTA_RAW       = "/home/jovyan/data/raw"
RUTA_PROCESSED = "/home/jovyan/data/processed"

ANIO_INICIO = 2010
ANIO_FIN    = 2026


# ── SparkSession ──────────────────────────────────────────────────
def crear_spark() -> SparkSession:
    """
    El JAR JDBC de PostgreSQL viene incluido en la imagen pyspark-notebook.
    Si no está disponible, descargarlo con:
      spark.jars.packages = org.postgresql:postgresql:42.7.1
    """
    return (
        SparkSession.builder
        .appName("mintic_transform")
        .config("spark.sql.shuffle.partitions", "8")
        .config(
            "spark.jars",
            "/home/jovyan/postgresql-42.7.3.jar",
        )
        .getOrCreate()
    )


# ── Helpers JDBC ──────────────────────────────────────────────────
def guardar_jdbc(df, tabla: str, modo: str = "append") -> None:
    """Escribe un DataFrame a PostgreSQL usando JDBC."""
    df.write.jdbc(
        url=JDBC_URL,
        table=tabla,
        mode=modo,
        properties=JDBC_PROPS,
    )
    print(f"    ✓ {tabla} — {df.count():,} filas guardadas ({modo})")


def leer_jdbc(spark: SparkSession, tabla: str):
    return spark.read.jdbc(url=JDBC_URL, table=tabla, properties=JDBC_PROPS)


# ── dim_periodo ───────────────────────────────────────────────────
def cargar_dim_periodo(spark: SparkSession) -> None:
    """
    Genera el calendario mes-año 2010-2026 y lo inserta en dim_periodo.
    Se usa overwrite para idempotencia.
    """
    print("  Generando dim_periodo...")
    filas = []
    for anio in range(ANIO_INICIO, ANIO_FIN + 1):
        for mes in range(1, 13):
            filas.append((anio, mes, date(anio, mes, 1)))

    esquema = StructType([
        StructField("anio",         IntegerType(), False),
        StructField("mes",          IntegerType(), False),
        StructField("fecha_inicio", DateType(),    False),
    ])
    df = spark.createDataFrame(filas, schema=esquema)

    # Evitar duplicados: solo insertar periodos que no existen aún
    try:
        existentes = leer_jdbc(spark, "dim_periodo").select("anio", "mes")
        df = df.join(existentes, on=["anio", "mes"], how="left_anti")
    except Exception:
        pass  # tabla vacía en primera ejecución

    n = df.count()
    if n > 0:
        df.write.jdbc(url=JDBC_URL, table="dim_periodo", mode="append", properties=JDBC_PROPS)
        print(f"    ✓ dim_periodo — {n:,} filas guardadas (append)")
    else:
        print("    ⏭ dim_periodo ya está completa")


# ── fact_demanda_sena ─────────────────────────────────────────────
def transformar_sena(spark: SparkSession) -> None:
    """
    Lee sena_inscritos.csv (formato datos.gov.co: inscritos 2019/2020 por ocupacion).
    Pivotea a filas anuales y carga a fact_demanda_sena.
    Columnas reales: nombre_de_la_ocupaci_n, nivel, n_mero_de_inscritos_2019,
                     n_mero_de_inscritos_2020, participacion_2019, participacion_2020,
                     variacion_2020_vs_2019, contribuci_n_a_la_variaci
    """
    ruta_csv = os.path.join(RUTA_RAW, "sena", "sena_inscritos.csv")
    print(f"  Transformando SENA: {ruta_csv}")

    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .option("encoding", "UTF-8")
        .csv(ruta_csv)
    )

    # Normalizar nombres a minúsculas
    for col in df.columns:
        df = df.withColumnRenamed(col, col.strip().lower().replace(" ", "_"))

    dim_periodo = leer_jdbc(spark, "dim_periodo").select("id_periodo", "anio", "mes")
    # Usar enero de cada año como periodo representativo (datos anuales)
    periodo_2019 = dim_periodo.filter((F.col("anio") == 2019) & (F.col("mes") == 1)) \
                              .select(F.col("id_periodo").alias("id_periodo_2019"))
    periodo_2020 = dim_periodo.filter((F.col("anio") == 2020) & (F.col("mes") == 1)) \
                              .select(F.col("id_periodo").alias("id_periodo_2020"))

    id_p2019 = periodo_2019.first()["id_periodo_2019"] if periodo_2019.count() > 0 else None
    id_p2020 = periodo_2020.first()["id_periodo_2020"] if periodo_2020.count() > 0 else None

    col_ocup  = "nombre_de_la_ocupaci_n" if "nombre_de_la_ocupaci_n" in df.columns else None
    col_nivel = "nivel" if "nivel" in df.columns else None
    col_i2019 = "n_mero_de_inscritos_2019" if "n_mero_de_inscritos_2019" in df.columns else None
    col_i2020 = "n_mero_de_inscritos_2020" if "n_mero_de_inscritos_2020" in df.columns else None

    filas_2019 = (
        df.select(
            F.lit(id_p2019).cast(IntegerType()).alias("id_periodo"),
            F.lit(None).cast(IntegerType()).alias("id_departamento"),
            F.col(col_ocup).alias("ocupacion") if col_ocup else F.lit(None).cast(StringType()).alias("ocupacion"),
            F.col(col_nivel).alias("sector_economico") if col_nivel else F.lit(None).cast(StringType()).alias("sector_economico"),
            F.col(col_i2019).cast(FloatType()).alias("inscritos") if col_i2019 else F.lit(None).cast(FloatType()).alias("inscritos"),
            F.lit(None).cast(FloatType()).alias("vacantes"),
        )
        .withColumn("fuente", F.lit("SENA"))
        .withColumn("fecha_carga", F.current_timestamp())
        .dropna(subset=["id_periodo"])
    )

    filas_2020 = (
        df.select(
            F.lit(id_p2020).cast(IntegerType()).alias("id_periodo"),
            F.lit(None).cast(IntegerType()).alias("id_departamento"),
            F.col(col_ocup).alias("ocupacion") if col_ocup else F.lit(None).cast(StringType()).alias("ocupacion"),
            F.col(col_nivel).alias("sector_economico") if col_nivel else F.lit(None).cast(StringType()).alias("sector_economico"),
            F.col(col_i2020).cast(FloatType()).alias("inscritos") if col_i2020 else F.lit(None).cast(FloatType()).alias("inscritos"),
            F.lit(None).cast(FloatType()).alias("vacantes"),
        )
        .withColumn("fuente", F.lit("SENA"))
        .withColumn("fecha_carga", F.current_timestamp())
        .dropna(subset=["id_periodo"])
    )

    df_final = filas_2019.unionAll(filas_2020)
    guardar_jdbc(df_final, "fact_demanda_sena", "append")


# ── fact_mercado_laboral (boletines parseados) ────────────────────
def transformar_serie_temporal(spark: SparkSession) -> None:
    """
    Lee serie_temporal_td.csv (generado por parsear_boletines.py),
    enriquece con id_periodo y carga a fact_mercado_laboral.
    Esto cubre los indicadores agregados nacionales (TD/TO/TGP).
    """
    ruta_csv = os.path.join(RUTA_PROCESSED, "serie_temporal_td.csv")
    if not os.path.exists(ruta_csv):
        print(f"  ⚠ No existe {ruta_csv} — ejecutar parsear_boletines.py primero")
        return

    print(f"  Transformando serie temporal: {ruta_csv}")

    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(ruta_csv)
    )

    dim_periodo = leer_jdbc(spark, "dim_periodo")
    df = df.join(
        dim_periodo.select("id_periodo", "anio", "mes"),
        on=["anio", "mes"],
        how="left",
    )

    df_final = (
        df.select(
            "id_periodo",
            F.lit(None).cast(IntegerType()).alias("id_departamento"),
            F.lit("Total").alias("sexo"),
            F.lit("Total").alias("grupo_edad"),
            F.lit("Total").alias("zona"),
            F.lit(None).cast(StringType()).alias("nivel_educativo"),
            F.lit(None).cast(StringType()).alias("rama_actividad"),
            F.lit(None).cast(StringType()).alias("posicion_ocupacional"),
            F.col("tasa_desocupacion").cast(FloatType()),
            F.col("tasa_ocupacion").cast(FloatType()),
            F.col("tasa_global_participacion").cast(FloatType()),
            F.lit(None).cast(FloatType()).alias("tasa_formalidad"),
            F.lit(None).cast(FloatType()).alias("tasa_informalidad"),
            F.lit(None).cast(FloatType()).alias("ingreso_laboral"),
            F.lit(None).cast(FloatType()).alias("afiliacion_seg_social"),
            F.col("variacion_anual_td").cast(FloatType()),
            F.lit("DANE_BOLETIN").alias("fuente"),
        )
        .withColumn("fecha_carga", F.current_timestamp())
        .dropna(subset=["id_periodo"])
    )

    guardar_jdbc(df_final, "fact_mercado_laboral", "append")


# ── fact_mercado_laboral (microdatos GEIH) ────────────────────────
def transformar_geih(spark: SparkSession) -> None:
    """
    Procesa los archivos ZIP/CSV del microdato GEIH descargados en data/raw/geih/.
    Limpia y carga a fact_mercado_laboral con granularidad individual.
    """
    dim_periodo = leer_jdbc(spark, "dim_periodo")
    dim_depto   = leer_jdbc(spark, "dim_departamento")

    for anio in ["2024", "2025"]:
        ruta_anio = os.path.join(RUTA_RAW, "geih", anio)
        if not os.path.exists(ruta_anio):
            print(f"  ⚠ Sin carpeta geih/{anio}/ — omitiendo")
            continue

        csvs = [f for f in os.listdir(ruta_anio) if f.lower().endswith(".csv")]
        if not csvs:
            print(f"  ⚠ Sin CSV en geih/{anio}/ — omitiendo")
            continue

        for nombre_csv in csvs:
            ruta_csv = os.path.join(ruta_anio, nombre_csv)
            print(f"  Procesando: {nombre_csv}")

            try:
                df = (
                    spark.read
                    .option("header", "true")
                    .option("inferSchema", "true")
                    .option("encoding", "UTF-8")
                    .csv(ruta_csv)
                )

                # Normalizar nombres
                for col in df.columns:
                    df = df.withColumnRenamed(col, col.strip().lower())

                # Los microdatos GEIH usan códigos DANE estándar
                # Columnas clave: p6020 (sexo), p6040 (edad), p6210 (educacion)
                # dpto (departamento), clase (zona 1=cabecera 2=resto)
                # inglabo (ingreso laboral), rama2d (rama actividad)
                # Estos nombres pueden variar por año — hacemos mapeo defensivo
                renombres = {
                    "p6020":   "sexo_cod",
                    "p6040":   "edad",
                    "p6210":   "nivel_educativo_cod",
                    "dpto":    "codigo_dane",
                    "clase":   "zona_cod",
                    "inglabo": "ingreso_laboral",
                    "rama2d":  "rama_actividad_cod",
                    "p6430":   "posicion_ocupacional_cod",
                }
                for orig, nuevo in renombres.items():
                    if orig in df.columns:
                        df = df.withColumnRenamed(orig, nuevo)

                # Decodificar sexo
                if "sexo_cod" in df.columns:
                    df = df.withColumn(
                        "sexo",
                        F.when(F.col("sexo_cod") == 1, "Hombre")
                         .when(F.col("sexo_cod") == 2, "Mujer")
                         .otherwise("Sin dato"),
                    )

                # Grupo de edad
                if "edad" in df.columns:
                    df = df.withColumn(
                        "grupo_edad",
                        F.when(F.col("edad").between(15, 28), "15-28")
                         .when(F.col("edad").between(29, 45), "29-45")
                         .when(F.col("edad") >= 46,           "46-65+")
                         .otherwise(None),
                    )

                # Zona
                if "zona_cod" in df.columns:
                    df = df.withColumn(
                        "zona",
                        F.when(F.col("zona_cod") == 1, "Cabecera")
                         .when(F.col("zona_cod") == 2, "Resto")
                         .otherwise("Sin dato"),
                    )

                # Unir periodo (el CSV debería tener columnas mes y año o las inferimos del nombre)
                df = df.withColumn("anio", F.lit(int(anio)).cast(IntegerType()))
                # Si hay columna mes en el CSV la usamos, si no asumimos promedio anual (mes=0 no existe)
                if "mes" not in df.columns:
                    df = df.withColumn("mes", F.lit(1).cast(IntegerType()))

                df = df.join(
                    dim_periodo.select("id_periodo", "anio", "mes"),
                    on=["anio", "mes"], how="left"
                )

                # Unir departamento
                if "codigo_dane" in df.columns:
                    df = df.withColumn("codigo_dane", F.lpad(F.col("codigo_dane").cast(StringType()), 2, "0"))
                    df = df.join(
                        dim_depto.select("id_departamento", "codigo_dane"),
                        on="codigo_dane", how="left"
                    )

                # Seleccionar columnas del modelo
                cols_disponibles = df.columns
                def col_o_null(nombre, tipo=StringType()):
                    return F.col(nombre) if nombre in cols_disponibles else F.lit(None).cast(tipo)

                df_final = df.select(
                    col_o_null("id_periodo",                IntegerType()),
                    col_o_null("id_departamento",           IntegerType()),
                    col_o_null("sexo"),
                    col_o_null("grupo_edad"),
                    col_o_null("zona"),
                    col_o_null("nivel_educativo_cod"),
                    col_o_null("rama_actividad_cod"),
                    col_o_null("posicion_ocupacional_cod"),
                    F.lit(None).cast(FloatType()).alias("tasa_desocupacion"),
                    F.lit(None).cast(FloatType()).alias("tasa_ocupacion"),
                    F.lit(None).cast(FloatType()).alias("tasa_global_participacion"),
                    F.lit(None).cast(FloatType()).alias("tasa_formalidad"),
                    F.lit(None).cast(FloatType()).alias("tasa_informalidad"),
                    col_o_null("ingreso_laboral",           FloatType()),
                    F.lit(None).cast(FloatType()).alias("afiliacion_seg_social"),
                    F.lit(None).cast(FloatType()).alias("variacion_anual_td"),
                    F.lit("GEIH").alias("fuente"),
                ).withColumn("fecha_carga", F.current_timestamp())

                # Filtrar solo registros con periodo válido
                df_final = df_final.dropna(subset=["id_periodo"])
                guardar_jdbc(df_final, "fact_mercado_laboral", "append")

            except Exception as e:
                print(f"    ✗ Error procesando {nombre_csv}: {e}")


# ── Entry point ───────────────────────────────────────────────────
def transformar():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando F3 · DataTransform...\n")
    spark = crear_spark()

    try:
        print("── dim_periodo ────────────────────────────────────────")
        cargar_dim_periodo(spark)

        print("\n── fact_demanda_sena (SENA) ────────────────────────────")
        transformar_sena(spark)

        print("\n── fact_mercado_laboral (boletines DANE) ──────────────")
        transformar_serie_temporal(spark)

        print("\n── fact_mercado_laboral (microdatos GEIH) ─────────────")
        transformar_geih(spark)

    finally:
        spark.stop()

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] DataTransform completado.")


if __name__ == "__main__":
    transformar()
