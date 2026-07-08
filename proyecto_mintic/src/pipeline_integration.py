"""Unión y consolidación de los conjuntos de datos del mercado laboral."""
import pandas as pd
from src.config import DATA_RAW, DATA_INTERMEDIATE, DATA_PRIMARY
from src.data_cleaning import clean_sena, clean_serie_temporal, remove_duplicates


def load_and_clean_serie() -> pd.DataFrame:
    """Carga y limpia la serie temporal DANE."""
    path = DATA_RAW.parent / "processed" / "serie_temporal_td.csv"
    df = pd.read_csv(path)
    df = clean_serie_temporal(df)
    df = remove_duplicates(df, subset=["fecha"])
    df.to_csv(DATA_INTERMEDIATE / "serie_temporal_limpia.csv", index=False)
    print(f"  Serie temporal: {len(df)} registros")
    return df


def load_and_clean_sena() -> pd.DataFrame:
    """Carga y limpia el dataset SENA."""
    path = DATA_RAW / "sena" / "sena_inscritos.csv"
    df = pd.read_csv(path)
    df = clean_sena(df)
    df = remove_duplicates(df, subset=["ocupacion"])
    df.to_csv(DATA_INTERMEDIATE / "sena_limpio.csv", index=False)
    print(f"  SENA: {len(df)} registros")
    return df


def build_consolidated_dataset(df_serie: pd.DataFrame, df_sena: pd.DataFrame) -> pd.DataFrame:
    """Une la serie temporal con totales SENA por año."""
    totales_sena = {}
    if "inscritos_2019" in df_sena.columns:
        totales_sena[2019] = int(df_sena["inscritos_2019"].sum())
    if "inscritos_2020" in df_sena.columns:
        totales_sena[2020] = int(df_sena["inscritos_2020"].sum())

    df = df_serie.copy()
    df["total_inscritos_sena"] = df["anio"].map(totales_sena)

    output_path = DATA_PRIMARY / "dataset_consolidado.csv"
    df.to_csv(output_path, index=False)
    print(f"  Dataset consolidado guardado: {output_path}")
    return df


def run_integration_pipeline() -> pd.DataFrame:
    """Ejecuta el pipeline completo de integración de datos."""
    print("=== Pipeline de Integración ===")
    df_serie = load_and_clean_serie()
    df_sena = load_and_clean_sena()
    df_consolidado = build_consolidated_dataset(df_serie, df_sena)
    print(f"  Consolidado final: {len(df_consolidado)} filas × {len(df_consolidado.columns)} columnas")
    return df_consolidado


if __name__ == "__main__":
    run_integration_pipeline()
